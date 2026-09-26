import unittest

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

from models.will_blockchain import (
    create_blockchain_event_model,
    create_blockchain_outbox_model,
    create_will_version_model,
)


class BlockchainModelSchemaTest(unittest.TestCase):
    def test_models_create_tables_and_constraints(self):
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db = SQLAlchemy(app)

        class Will(db.Model):
            __tablename__ = 'wills'

            id = db.Column(db.Integer, primary_key=True)

        create_will_version_model(db)
        create_blockchain_event_model(db)
        create_blockchain_outbox_model(db)

        with app.app_context():
            db.create_all()
            schema = inspect(db.engine)

            self.assertTrue({
                'wills_versions',
                'blockchain_events',
                'blockchain_outbox',
            }.issubset(set(schema.get_table_names())))

            version_constraints = schema.get_unique_constraints('wills_versions')
            self.assertIn(
                ['will_id', 'version'],
                [constraint['column_names'] for constraint in version_constraints],
            )

            outbox_foreign_keys = schema.get_foreign_keys('blockchain_outbox')
            self.assertTrue(any(
                foreign_key['referred_table'] == 'wills_versions'
                for foreign_key in outbox_foreign_keys
            ))

            db.drop_all()


if __name__ == '__main__':
    unittest.main()