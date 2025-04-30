import qrcode
import uuid  # For generating unique transaction IDs

def generate_payment_qr_code(payee_vpa, amount, payee_name="Merchant", transaction_id=None):
    """
    Generates a QR code for a payment request.  This generates a BharatQR-like
    QR code string.  For real-world use, integrate with a payment gateway.

    Args:
        payee_vpa (str):  Payee's Virtual Payment Address (e.g., user@bank).
        amount (float): Amount to be paid.
        payee_name (str, optional): Name of the payee/merchant. Defaults to "Merchant".
        transaction_id (str, optional): Unique transaction ID. If None, a random one is generated.

    Returns:
        qrcode.QRCode: QR Code object
    """
    if transaction_id is None:
        transaction_id = str(uuid.uuid4())  # Generate a unique transaction ID

    #  Simplified BharatQR format.  Consult official specs for full details and supported parameters.
    qr_string = f"upi://pay?pa={payee_vpa}&pn={payee_name}&tid={transaction_id}&am={amount:.2f}&cu=INR"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_string)
    qr.make(fit=True)
    return qr, qr_string  # Return both the QRCode object and the string

def display_qr_code(qr_code):
    """
    Displays the QR code in the terminal.  This requires the 'qrencode'
    command-line utility to be installed.  If qrencode is not available,
    it will print a URL that can be used to view the QR code online.

    Args:
        qr_code (qrcode.QRCode): The QR code object to display.
    """
    try:
        import subprocess
        # Convert the QR code to a string
        qr_str = qr_code.get_matrix()
        # Use qrencode to display the QR code in the terminal
        subprocess.run(['qrencode', '-t', 'utf8', qr_code.qr_code.encode()], input=qr_code_str.encode(), check=True)

    except FileNotFoundError:
        # qrencode is not installed, provide a URL for online viewing
        img = qr_code.make_image()
        # Generate a data URI for the QR code image
        import io
        import base64
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        print("Please install qrencode to view QR code in terminal, or use this URL:")
        print(f"https://qrcodegenerator.com/?data=data:image/png;base64,{img_base64}")

    except Exception as e:
        print(f"Error displaying QR code: {e}")
        print("You can save the QR code to a file and view it that way.")

def save_qr_code(qr_code, filename="payment_qr_code.png"):
    """
    Saves the QR code as a PNG image.

    Args:
        qr_code (qrcode.QRCode): The QR code object to save.
        filename (str, optional): The name of the file to save.
            Defaults to "payment_qr_code.png".
    """
    img = qr_code.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"QR code saved to {filename}")

if __name__ == "__main__":
    payee_vpa = "7904030221@ptsbi"  # Replace with your VPA.  This is a *sample*.
    amount = 100.00  # Amount in Rupees
    payee_name = "My Merchant" #Replace Merchant Name
    # Generate a unique transaction ID (Important for tracking)
    transaction_id = "TXN" + str(uuid.uuid4())

    qr_code, qr_string = generate_payment_qr_code(payee_vpa, amount, payee_name, transaction_id)

    print(f"QR Code Data (for reference, not directly scannable in most apps): {qr_string}") #print the data

    # Save the QR code as an image file
    save_qr_code(qr_code)

    # Display the QR code in the terminal (requires 'qrencode')
    display_qr_code(qr_code)
