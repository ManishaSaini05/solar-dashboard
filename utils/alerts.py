# # ============================================================
# #  utils/alerts.py — Email notification helpers
# # ============================================================

# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from datetime import datetime
# from config import EMAIL_USER, EMAIL_PASSWORD, TO_EMAILS


# def send_email_alert(brand: str, plant: str, inverter_sn: str, issue: str) -> bool:
#     """
#     Send an HTML alert email.
#     Returns True on success, False on failure.
#     """
#     try:
#         subject = f"🚨 Solar Alert — {plant} [{brand}]"

#         html = f"""
#         <html><body style="font-family:Arial,sans-serif;background:#f4f4f4;padding:20px;">
#           <div style="max-width:600px;margin:auto;background:#fff;border-radius:8px;
#                       box-shadow:0 2px 8px rgba(0,0,0,.1);overflow:hidden;">
#             <div style="background:#d32f2f;padding:20px;color:#fff;">
#               <h2 style="margin:0;">⚡ Solar Inverter Alert</h2>
#             </div>
#             <div style="padding:24px;">
#               <table style="width:100%;border-collapse:collapse;">
#                 <tr><td style="padding:8px;color:#666;width:140px;">Brand</td>
#                     <td style="padding:8px;font-weight:bold;">{brand}</td></tr>
#                 <tr style="background:#f9f9f9;">
#                     <td style="padding:8px;color:#666;">Plant</td>
#                     <td style="padding:8px;font-weight:bold;">{plant}</td></tr>
#                 <tr><td style="padding:8px;color:#666;">Inverter S/N</td>
#                     <td style="padding:8px;font-weight:bold;">{inverter_sn}</td></tr>
#                 <tr style="background:#f9f9f9;">
#                     <td style="padding:8px;color:#666;">Issue</td>
#                     <td style="padding:8px;color:#d32f2f;font-weight:bold;">{issue}</td></tr>
#                 <tr><td style="padding:8px;color:#666;">Time</td>
#                     <td style="padding:8px;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
#               </table>
#               <p style="margin-top:20px;color:#888;font-size:13px;">
#                 This alert was generated automatically by your Solar Dashboard.
#                 Please log in to investigate.
#               </p>
#             </div>
#           </div>
#         </body></html>
#         """

#         msg = MIMEMultipart("alternative")
#         msg["Subject"] = subject
#         msg["From"]    = EMAIL_USER
#         msg["To"]      = ", ".join(TO_EMAILS)
#         msg.attach(MIMEText(html, "html"))

#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()
#             server.login(EMAIL_USER, EMAIL_PASSWORD)
#             server.sendmail(EMAIL_USER, TO_EMAILS, msg.as_string())

#         return True

#     except Exception as e:
#         print(f"❌ Email error: {e}")
#         return False

# utils/alerts.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from config import EMAIL_USER, EMAIL_PASSWORD, TO_EMAILS

def send_email_alert(brand, plant, sn, issue):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 Solar Alert — {plant} [{brand}]"
        msg["From"]    = EMAIL_USER
        msg["To"]      = ", ".join(TO_EMAILS)
        msg.attach(MIMEText(f"""
        <html><body style="font-family:Inter,sans-serif;background:#f4f4f4;padding:20px;">
          <div style="max-width:560px;margin:auto;background:#fff;border-radius:10px;overflow:hidden;">
            <div style="background:#f5821f;padding:20px 24px;">
              <h2 style="margin:0;color:#fff;font-size:18px;">⚡ Solar Inverter Alert</h2>
            </div>
            <div style="padding:24px;">
              <table style="width:100%;border-collapse:collapse;font-size:14px;">
                <tr><td style="padding:8px;color:#666;width:130px;">Brand</td><td style="padding:8px;font-weight:600;">{brand}</td></tr>
                <tr style="background:#f9f9f9;"><td style="padding:8px;color:#666;">Plant</td><td style="padding:8px;font-weight:600;">{plant}</td></tr>
                <tr><td style="padding:8px;color:#666;">Inverter S/N</td><td style="padding:8px;font-weight:600;">{sn}</td></tr>
                <tr style="background:#f9f9f9;"><td style="padding:8px;color:#666;">Issue</td><td style="padding:8px;font-weight:600;color:#e84855;">{issue}</td></tr>
                <tr><td style="padding:8px;color:#666;">Time</td><td style="padding:8px;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
              </table>
            </div>
          </div>
        </body></html>""", "html"))
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls(); s.login(EMAIL_USER, EMAIL_PASSWORD)
            s.sendmail(EMAIL_USER, TO_EMAILS, msg.as_string())
        return True
    except Exception as e:
        print(f"❌ Email: {e}"); return False