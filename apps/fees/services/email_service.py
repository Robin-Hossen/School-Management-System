from django.core.mail import send_mail


def send_payment_confirmation(
    payment,
    notification="NONE",
):
    """
    Send payment confirmation email
    to student, guardian or both.
    """

    # ---------------------------------
    # No notification
    # ---------------------------------

    if notification == "NONE":
        return {
            "student": False,
            "guardian": False,
        }

    student = payment.student_fee.student

    student_email = student.user.email
    guardian_email = student.guardian_email

    student_name = student.user.get_full_name()
    student_code = student.student_id

    fee_name = payment.student_fee.fee_structure.name

    subject = "Fee Payment Confirmation"

    message = f"""
Dear Parent/Student,

Your fee payment has been successfully recorded.

Student Name: {student_name}
Student ID: {student_code}

Fee: {fee_name}

Amount Paid: {payment.amount}
Payment Date: {payment.payment_date}
Payment Method: {payment.payment_method}

Transaction ID: {payment.transaction_id or "N/A"}

Remarks: {payment.remarks or "N/A"}

Thank you.

School Management System
"""

    recipients = []

    if notification in ("STUDENT", "BOTH"):
        if student_email:
            recipients.append(student_email)

    if notification in ("GUARDIAN", "BOTH"):
        if guardian_email:
            recipients.append(guardian_email)

    # Remove duplicate emails
    recipients = list(set(recipients))

    if not recipients:
        return {
            "student": False,
            "guardian": False,
            "message": "No valid email address found.",
        }

    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=recipients,
        fail_silently=False,
    )

    return {
        "student": (
            notification in ("STUDENT", "BOTH")
            and bool(student_email)
        ),
        "guardian": (
            notification in ("GUARDIAN", "BOTH")
            and bool(guardian_email)
        ),
    }