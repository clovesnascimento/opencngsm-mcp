"""
OpenCngsm v3.0 - PIX Skill
Native Python implementation for Brazilian payment QR codes
"""
import qrcode
from io import BytesIO
from typing import Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PIXSkill:
    """
    PIX payment QR code generator for Brazil
    
    Features:
    - Generate static PIX QR codes
    - BR Code payload generation
    - CRC16 validation
    - QR code image generation
    - Support for all PIX key types (CPF, CNPJ, email, phone, random)
    """
    
    def __init__(self, nome: str = 'Recebedor', cidade: str = 'Fortaleza'):
        """
        Initialize PIX skill
        
        Args:
            nome: Receiver name (max 25 chars)
            cidade: Receiver city (max 15 chars)
        """
        self.nome = nome[:25]
        self.cidade = cidade[:15]
    
    def calculate_crc16(self, payload: str) -> str:
        """
        Calculate CRC16 for PIX payload validation
        Uses CRC-16/CCITT-FALSE polynomial
        
        Args:
            payload: Payload string without CRC
        
        Returns:
            4-digit hex CRC string
        """
        crc = 0xFFFF
        poly = 0x1021
        
        for char in payload:
            crc ^= ord(char) << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ poly
                else:
                    crc <<= 1
                crc &= 0xFFFF
        
        return format(crc, '04X')
    
    def generate_static_payload(
        self,
        chave: str,
        valor: float,
        descricao: str = '',
        identificador: str = '***'
    ) -> str:
        """
        Generate PIX static payload (BR Code format)
        
        Args:
            chave: PIX key (CPF, CNPJ, email, phone, or random key)
            valor: Amount in BRL (e.g., 49.90)
            descricao: Transaction description
            identificador: Transaction identifier
        
        Returns:
            Complete BR Code payload string
        
        Example:
            payload = pix.generate_static_payload(
                chave='seuemail@gmail.com',
                valor=49.90,
                descricao='Pagamento pedido #1234'
            )
        """
        parts = []
        
        # 00 - Payload Format Indicator
        parts.append('000201')
        
        # 01 - Point of Initiation Method (12 = static)
        parts.append('010212')
        
        # 26 - Merchant Account Information
        pix_gui = 'br.gov.bcb.pix'
        pix_key_data = f"0014{pix_gui}01{len(chave):02d}{chave}"
        parts.append(f"26{len(pix_key_data):02d}{pix_key_data}")
        
        # 52 - Merchant Category Code
        parts.append('52040000')
        
        # 53 - Transaction Currency (986 = BRL)
        parts.append('5303986')
        
        # 54 - Transaction Amount
        valor_str = f"{valor:.2f}"
        parts.append(f"54{len(valor_str):02d}{valor_str}")
        
        # 58 - Country Code
        parts.append('5802BR')
        
        # 59 - Merchant Name
        if self.nome:
            parts.append(f"59{len(self.nome):02d}{self.nome}")
        
        # 60 - Merchant City
        if self.cidade:
            parts.append(f"60{len(self.cidade):02d}{self.cidade}")
        
        # 62 - Additional Data Field
        ad_parts = []
        if identificador:
            ad_parts.append(f"05{len(identificador):02d}{identificador}")
        if descricao:
            ad_parts.append(f"07{len(descricao):02d}{descricao}")
        
        if ad_parts:
            ad_data = ''.join(ad_parts)
            parts.append(f"62{len(ad_data):02d}{ad_data}")
        
        # Calculate CRC
        payload_sem_crc = ''.join(parts)
        crc = self.calculate_crc16(payload_sem_crc + '6304')
        
        final_payload = payload_sem_crc + f"6304{crc}"
        
        logger.info(f"✅ PIX payload generated for R$ {valor:.2f}")
        return final_payload
    
    def generate_qr_code(
        self,
        chave: str,
        valor: float,
        descricao: str = '',
        size: int = 10,
        output_path: Optional[Union[str, Path]] = None
    ) -> BytesIO:
        """
        Generate PIX QR code image
        
        Args:
            chave: PIX key
            valor: Amount in BRL
            descricao: Transaction description
            size: QR code box size (default 10)
            output_path: Optional path to save image file
        
        Returns:
            BytesIO buffer with PNG image
        
        Example:
            # Generate and save
            buffer = pix.generate_qr_code(
                chave='seuemail@gmail.com',
                valor=49.90,
                output_path='qrcode.png'
            )
            
            # Or use buffer directly
            from PIL import Image
            img = Image.open(buffer)
            img.show()
        """
        # Generate payload
        payload = self.generate_static_payload(chave, valor, descricao)
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=4
        )
        qr.add_data(payload)
        qr.make(fit=True)
        
        # Generate image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(buffer.getvalue())
            logger.info(f"✅ QR code saved to {output_path}")
            buffer.seek(0)  # Reset buffer position
        
        logger.info(f"✅ PIX QR code generated for R$ {valor:.2f}")
        return buffer
    
    def validate_payload(self, payload: str) -> bool:
        """
        Validate PIX payload CRC
        
        Args:
            payload: Complete BR Code payload
        
        Returns:
            True if CRC is valid
        """
        try:
            if len(payload) < 4:
                return False
            
            # Extract CRC from payload
            payload_sem_crc = payload[:-4]
            crc_fornecido = payload[-4:]
            
            # Calculate expected CRC
            crc_calculado = self.calculate_crc16(payload_sem_crc)
            
            return crc_fornecido == crc_calculado
        except Exception as e:
            logger.error(f"❌ Failed to validate payload: {e}")
            return False


# Skill metadata
SKILL_NAME = "pix"
SKILL_CLASS = PIXSkill
SKILL_DESCRIPTION = "Generate PIX payment QR codes for Brazilian transactions"


# Auto-register
from . import register_skill
register_skill(SKILL_NAME, SKILL_CLASS, SKILL_DESCRIPTION)
