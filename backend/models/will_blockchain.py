from datetime import datetime


def create_will_version_model(db):
    class WillVersion(db.Model):
        __tablename__ = 'wills_versions'
        __table_args__ = (
            db.UniqueConstraint('will_id', 'version', name='uq_wills_versions_will_version'),
            db.Index('idx_wills_versions_latest', 'will_id', 'version'),
        )

        id = db.Column(db.BigInteger, primary_key=True)
        will_id = db.Column(db.Integer, db.ForeignKey('wills.id'), nullable=False)
        version = db.Column(db.Integer, nullable=False)
        pdf_path = db.Column(db.String(1024), nullable=False)
        hash = db.Column(db.CHAR(64), nullable=False)
        blockchain_tx = db.Column(db.String(66))
        blockchain_status = db.Column(
            db.Enum('pending', 'submitted', 'confirmed', 'failed'),
            nullable=False,
            default='pending',
        )
        blockchain_block = db.Column(db.BigInteger)
        encryption_key_id = db.Column(db.String(255), nullable=False)
        encryption_nonce = db.Column(db.LargeBinary(12), nullable=False)
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        confirmed_at = db.Column(db.DateTime)

    return WillVersion


def create_blockchain_event_model(db):
    class BlockchainEvent(db.Model):
        __tablename__ = 'blockchain_events'
        __table_args__ = (
            db.Index('idx_blockchain_events_will_created', 'will_id', 'created_at'),
            db.Index('idx_blockchain_events_tx', 'tx_hash'),
        )

        id = db.Column(db.BigInteger, primary_key=True)
        will_id = db.Column(db.Integer, db.ForeignKey('wills.id'), nullable=False)
        event_type = db.Column(db.String(64), nullable=False)
        tx_hash = db.Column(db.String(66))
        payload = db.Column(db.JSON, nullable=False)
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    return BlockchainEvent


def create_blockchain_outbox_model(db):
    class BlockchainOutbox(db.Model):
        __tablename__ = 'blockchain_outbox'
        __table_args__ = (
            db.UniqueConstraint(
                'will_version_id', 'event_type', name='uq_blockchain_outbox_version_event'
            ),
            db.Index('idx_blockchain_outbox_ready', 'status', 'available_at'),
        )

        id = db.Column(db.BigInteger, primary_key=True)
        will_version_id = db.Column(
            db.BigInteger, db.ForeignKey('wills_versions.id'), nullable=False
        )
        event_type = db.Column(db.String(64), nullable=False)
        payload = db.Column(db.JSON, nullable=False)
        status = db.Column(
            db.Enum('pending', 'processing', 'completed', 'failed'),
            nullable=False,
            default='pending',
        )
        attempt_count = db.Column(db.Integer, nullable=False, default=0)
        available_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        locked_at = db.Column(db.DateTime)
        locked_by = db.Column(db.String(128))
        last_error = db.Column(db.Text)
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        updated_at = db.Column(
            db.DateTime,
            nullable=False,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
        )
        completed_at = db.Column(db.DateTime)

    return BlockchainOutbox