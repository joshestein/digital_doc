import unittest
from app import create_app, db
from app.models import Doctor, Patient
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class DoctorModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        d = Doctor(name = 'Dan')
        d.set_password('foo')
        self.assertFalse(d.check_password('bar'))
        self.assertTrue(d.check_password('foo'))

    def test_doctor_has_patient(self):
        d1 = Doctor(name = 'Gabi')
        d2 = Doctor(name = 'Dan')

        p1 = Patient(first_name = 'Josh', age = 22)
        p2 = Patient(first_name = 'Kelsey', age = 27)

        db.session.add_all([d1, d2, p1, p2])
        db.session.commit()
        self.assertEqual(d1.patients.all(), [])
        self.assertEqual(d2.patients.all(), [])

        d1.add_patient(p1)
        db.session.commit()
        self.assertTrue(d1.has_patient(p1))
        self.assertEqual(d1.patients.count(), 1)
        self.assertEqual(d1.patients.first().first_name, 'Josh')

        self.assertFalse(d2.has_patient(p1))
        self.assertEqual(d2.patients.count(), 0)

        d1.add_patient(p2)
        db.session.commit()
        patients = d1.get_all_patients().all()
        self.assertEqual(patients, [p1, p2])

        d1.remove_patient(p1)
        db.session.commit()
        self.assertFalse(d1.has_patient(p1))
        self.assertTrue(d1.has_patient(p2))
        self.assertEqual(d1.patients.count(), 1)

        d1.remove_patient(p2)
        db.session.commit()
        self.assertFalse(d1.has_patient(p2))
        self.assertEqual(d1.patients.count(), 0)

    def test_patient_has_doctor(self):
        d1 = Doctor(name = 'Stefan')
        d2 = Doctor(name = 'Dan')
        p1 = Patient(first_name = 'Kelsey')
        p2 = Patient(first_name = 'Josh')

        db.session.add_all([d1, d2, p1, p2])
        db.session.commit()

        self.assertEqual(p1.doctors.all(), [])
        self.assertEqual(p2.doctors.all(), [])

        p1.add_doctor(d1)
        db.session.commit()
        self.assertTrue(p1.has_doctor(d1))
        self.assertEqual(p1.doctors.count(), 1)
        self.assertEqual(p1.doctors.first().name, 'Stefan')

        self.assertFalse(p2.has_doctor(d1))
        self.assertEqual(p2.doctors.count(), 0)

        p1.add_doctor(d2)
        db.session.commit()
        doctors = p1.get_all_doctors().all()
        self.assertEqual(doctors, [d1, d2])

        p1.remove_doctor(d1)
        db.session.commit()
        self.assertFalse(p1.has_doctor(d1))
        self.assertTrue(p1.has_doctor(d2))
        self.assertEqual(p1.doctors.count(), 1)

        p1.remove_doctor(d2)
        db.session.commit()
        self.assertFalse(p1.has_doctor(d2))
        self.assertEqual(p1.doctors.count(), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
