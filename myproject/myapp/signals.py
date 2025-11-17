# myapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LandRequest, LandRequestHistory
from .blockchain_api import create_land_request , update_land_status # Make sure you have created this helper module
import uuid
import hashlib
import random


@receiver(post_save, sender=LandRequest)
def send_land_request_to_blockchain(sender, instance, created, **kwargs):
    print(f"[DEBUG] Signal triggered for: {instance.receipt_number}, created={created}")  # ✅ Add this

    if created:
        # Prepare a dictionary of the land request data.
        # Adjust the keys to match your chaincode's expected fields.
        
        if not instance.ipfs_hash:
            # Randomly mimic an IPFS CID format
            random_bytes = uuid.uuid4().bytes
            instance.ipfs_hash = hashlib.sha256(random_bytes).hexdigest()[:46]
            instance.save(update_fields=["ipfs_hash"])

        if not instance.txn_id:
            # Simple UUID-based transaction ID
            instance.txn_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
            instance.save(update_fields=["txn_id"])

        land_data = {
    "full_name": instance.full_name,
    "email": instance.email,
    "phone_number": instance.phone_number,
    "aadhar_number": instance.aadhar_number,
    "dob": instance.dob.isoformat() if instance.dob else None,
    "owner_name": instance.owner_name,
    "survey_number": instance.survey_number,
    "area": instance.area,
    "address": instance.address,
    "state": instance.state,
    "city": instance.city,
    "pincode": instance.pincode,
    "status": instance.status,
    "currently_with": instance.currently_with.username if instance.currently_with else None,
    "ipfs_hash": instance.ipfs_hash,
    "txn_id": instance.txn_id
}
        try:
            print("📤 Sending to blockchain...")
            result = create_land_request(instance.receipt_number, land_data)
            print("✅ Blockchain API result:", result)
        except Exception as e:
            print("❌ Blockchain API call failed:", e)



@receiver(post_save, sender=LandRequestHistory)
def send_land_history_to_blockchain(sender, instance, created, **kwargs):
    if created:
        receipt_number = instance.land_request.receipt_number
        new_status = instance.land_request.status
        assigned_to = instance.to_user.username if instance.to_user else ""
        remarks = instance.remarks or ""
        from_user = instance.from_user.username if instance.from_user else ""
        timestamp = instance.timestamp.isoformat()  # assuming field is 'timestamp'

        print(f"[DEBUG] Updating blockchain for: {receipt_number}")
        result = update_land_status(receipt_number, new_status, assigned_to, remarks, from_user, timestamp)
        print("📦 Blockchain update result:", result)
