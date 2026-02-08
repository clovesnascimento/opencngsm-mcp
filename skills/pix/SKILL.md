---
name: pix
description: Generate Brazilian PIX payment QR codes with BR Code format, CRC16 validation, and QR code image generation. Use when user mentions PIX, Brazilian payments, or QR code generation.
license: MIT
metadata:
  author: opencngsm
  version: "3.0"
  requires: qrcode==7.4.2, Pillow==10.1.0
compatibility: Brazil-specific payment system
---

# PIX Skill

## When to use this skill

Use this skill when the user wants to:
- Generate PIX payment QR codes
- Create BR Code (PIX code format)
- Generate QR code images for payments
- Validate PIX codes
- Accept Brazilian payments

## Setup

1. **Install dependencies:**
   ```bash
   pip install qrcode==7.4.2 Pillow==10.1.0
   ```

2. **Get PIX key:**
   - Can be: CPF, CNPJ, email, phone, or random key
   - Register in your bank app

## How to use

### Generate PIX QR code

```python
from skills.pix.pix_skill import PIXSkill

pix = PIXSkill(
    nome='Minha Loja',
    cidade='Fortaleza'
)

# Generate QR code
pix.generate_qr_code(
    chave='email@example.com',  # PIX key
    valor=49.90,                 # Amount in BRL
    descricao='Produto XYZ',     # Description
    output_path='pix_qrcode.png'
)
```

### Generate BR Code only

```python
# Get BR Code string
br_code = pix.generate_br_code(
    chave='11999999999',  # Phone number
    valor=100.00,
    descricao='Pagamento'
)

print(f"BR Code: {br_code}")
# User can copy and paste in bank app
```

### Validate PIX code

```python
# Validate BR Code
is_valid = pix.validate_br_code(br_code)
print(f"Valid: {is_valid}")
```

## Features

- ✅ Generate BR Code (PIX format)
- ✅ CRC16 validation
- ✅ QR code image generation
- ✅ Support all PIX key types (CPF, CNPJ, email, phone, random)
- ✅ Optional description
- ✅ Amount specification
- ✅ Merchant info (name, city)
- ✅ Validate existing codes

## PIX Key Types

- **CPF**: `12345678900`
- **CNPJ**: `12345678000100`
- **Email**: `email@example.com`
- **Phone**: `+5511999999999` or `11999999999`
- **Random**: `123e4567-e89b-12d3-a456-426614174000`

## BR Code Format

```
00020126...  # EMV format
52040000     # Merchant category
5303986      # Currency (BRL)
5405100.00   # Amount
5802BR       # Country
5913Merchant  # Name
6008City     # City
6304XXXX     # CRC16
```

## Implementation

See [pix_skill.py](pix_skill.py) for the complete implementation.

## Examples

```python
# Example 1: Simple payment
pix = PIXSkill(nome='Loja ABC', cidade='São Paulo')
pix.generate_qr_code(
    chave='loja@abc.com',
    valor=25.50,
    output_path='payment.png'
)

# Example 2: No amount (user enters)
pix.generate_qr_code(
    chave='11987654321',
    valor=0,  # User will enter amount
    descricao='Doação',
    output_path='donation.png'
)

# Example 3: Get code for manual entry
code = pix.generate_br_code(
    chave='12345678900',
    valor=150.00
)
# User copies code to bank app
```

## Troubleshooting

### "Invalid PIX key"
- Verify key format (CPF, email, phone, etc.)
- Check for typos
- Ensure key is registered in bank

### "QR code generation failed"
- Install Pillow: `pip install Pillow`
- Check output path permissions
- Verify disk space

### "CRC validation failed"
- BR Code may be corrupted
- Regenerate code
- Check for copy/paste errors

## Security

- ⚠️ Never share PIX keys publicly without consent
- ✅ Validate amounts before generating codes
- ✅ Use HTTPS for QR code transmission
- ✅ Verify recipient before payment

## References

- [PIX BR Code Specification](https://www.bcb.gov.br/estabilidadefinanceira/pix)
- [Banco Central do Brasil - PIX](https://www.bcb.gov.br/estabilidadefinanceira/pix)
