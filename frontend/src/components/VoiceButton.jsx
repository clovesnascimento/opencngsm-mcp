import React, { useState, useRef, useEffect } from 'react';
import './VoiceButton.css';

/**
 * VoiceButton Component
 * 
 * Push-to-talk button for voice input
 * Features:
 * - Microphone recording
 * - Audio visualization
 * - Automatic transcription
 * - Error handling
 */
const VoiceButton = ({
    onTranscript,
    onError,
    apiUrl = '/api/voice/transcribe',
    language = 'pt',
    className = ''
}) => {
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState(null);
    const [audioLevel, setAudioLevel] = useState(0);

    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const audioContextRef = useRef(null);
    const analyserRef = useRef(null);
    const animationFrameRef = useRef(null);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopRecording();
            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current);
            }
        };
    }, []);

    // Start recording
    const startRecording = async () => {
        try {
            setError(null);

            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 16000
                }
            });

            // Setup audio context for visualization
            audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
            analyserRef.current = audioContextRef.current.createAnalyser();
            const source = audioContextRef.current.createMediaStreamSource(stream);
            source.connect(analyserRef.current);
            analyserRef.current.fftSize = 256;

            // Start visualization
            visualizeAudio();

            // Setup MediaRecorder
            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                // Stop visualization
                if (animationFrameRef.current) {
                    cancelAnimationFrame(animationFrameRef.current);
                }
                setAudioLevel(0);

                // Create audio blob
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

                // Send to backend for transcription
                await transcribeAudio(audioBlob);

                // Cleanup
                stream.getTracks().forEach(track => track.stop());
                if (audioContextRef.current) {
                    audioContextRef.current.close();
                }
            };

            mediaRecorder.start();
            mediaRecorderRef.current = mediaRecorder;
            setIsRecording(true);

        } catch (err) {
            console.error('Failed to start recording:', err);
            const errorMsg = err.name === 'NotAllowedError'
                ? 'Microphone access denied. Please allow microphone access.'
                : 'Failed to access microphone.';
            setError(errorMsg);
            if (onError) onError(err);
        }
    };

    // Stop recording
    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    // Visualize audio levels
    const visualizeAudio = () => {
        if (!analyserRef.current) return;

        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);

        const updateLevel = () => {
            analyserRef.current.getByteFrequencyData(dataArray);

            // Calculate average volume
            const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
            setAudioLevel(Math.min(100, (average / 255) * 100));

            animationFrameRef.current = requestAnimationFrame(updateLevel);
        };

        updateLevel();
    };

    // Transcribe audio via API
    const transcribeAudio = async (audioBlob) => {
        setIsProcessing(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            formData.append('language', language);

            const response = await fetch(apiUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    // Don't set Content-Type - browser will set it with boundary
                }
            });

            if (!response.ok) {
                throw new Error(`Transcription failed: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.transcription) {
                if (onTranscript) {
                    onTranscript(data.transcription);
                }
            } else {
                throw new Error('No transcription returned');
            }

        } catch (err) {
            console.error('Transcription error:', err);
            setError('Failed to transcribe audio. Please try again.');
            if (onError) onError(err);
        } finally {
            setIsProcessing(false);
        }
    };

    // Handle mouse/touch events
    const handleMouseDown = (e) => {
        e.preventDefault();
        startRecording();
    };

    const handleMouseUp = (e) => {
        e.preventDefault();
        stopRecording();
    };

    return (
        <div className={`voice-button-container ${className}`}>
            <button
                className={`voice-button ${isRecording ? 'recording' : ''} ${isProcessing ? 'processing' : ''}`}
                onMouseDown={handleMouseDown}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
                onTouchStart={handleMouseDown}
                onTouchEnd={handleMouseUp}
                disabled={isProcessing}
                aria-label={isRecording ? 'Recording... Release to stop' : 'Hold to record voice'}
            >
                {isProcessing ? (
                    <div className="spinner" />
                ) : (
                    <>
                        <svg
                            className="mic-icon"
                            viewBox="0 0 24 24"
                            fill="currentColor"
                        >
                            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                        </svg>

                        {isRecording && (
                            <div className="audio-visualizer">
                                <div
                                    className="audio-level"
                                    style={{ height: `${audioLevel}%` }}
                                />
                            </div>
                        )}
                    </>
                )}
            </button>

            <div className="voice-button-status">
                {isRecording && <span className="status-text recording">🔴 Recording...</span>}
                {isProcessing && <span className="status-text processing">⏳ Transcribing...</span>}
                {!isRecording && !isProcessing && (
                    <span className="status-text idle">🎤 Hold to talk</span>
                )}
            </div>

            {error && (
                <div className="voice-button-error">
                    ⚠️ {error}
                </div>
            )}
        </div>
    );
};

export default VoiceButton;
