import unittest
import json
from datetime import datetime
import decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import StatementError, IntegrityError

from models.models import IngestedData, IngestionJobs, Base

class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        """

        Returns:

        Todo:
            * need to update the date assertions or just dumps the data to an object? those will always fail

        """
        self.record1 = {'val': 1.2}
        date1 = datetime(2021, 12, 17, 18, 35, 56, 11182)
        date2 = datetime(2021, 12, 17, 21, 45, 28, 479312)
        self.ingestion_jobs_input1 = {'uid':1, 'shorttext': 'test text', 'filename': 'myfile.csv', 'children': [{'val': 1.5}, {'val': 3}]}
        self.ingestion_jobs_output1 = "[{'shorttext': 'test text', 'uid': 1, 'filename': 'myfile.csv', 'benfords_result': None, 'children': [{'uid': 1, 'parent_id': 1, 'val': Decimal('1.5000000000')}, {'uid': 2, 'parent_id': 1, 'val': Decimal('3.0000000000')}]}]"
        self.ingestion_jobs_input2 = {'uid':2, 'shorttext': 'j2 test', 'filename': 'myfile.txt', 'children': [{'val': -0.5}, {'val': 0.5}]}
        self.ingestion_jobs_output2 = "[{'shorttext': 'j2 test', 'uid': 2, 'filename': 'myfile.txt', 'ingested_date': datetime.datetime(2021, 12, 17, 21, 45, 28, 479312), 'benfords_result': None, 'children': [{'uid': 1, 'parent_id': 1, 'val': Decimal('-0.5000000000')}, {'uid': 2, 'parent_id': 1, 'val': Decimal('0.5000000000')}]}]"
        self.ingested_data_input1 = {'val': 3.0, 'parent_id':1}
        self.ingested_data_input2 = {'val': 10, 'parent_id':1}
        self.ingested_data_output1 = "{'uid': 5, 'parent_id': 1, 'val': Decimal('3.0000000000'), 'parent': {'shorttext': 'test text', 'uid': 1, 'filename': 'myfile.csv', 'ingested_date': datetime.datetime(2021, 12, 17, 18, 35, 56, 11182), 'benfords_result': None}}"
        self.ingested_data_output2 = "{'uid': 6, 'parent_id': 1, 'val': Decimal('10.0000000000'), 'parent': {'shorttext': 'test text', 'uid': 1, 'filename': 'myfile.csv', 'ingested_date': datetime.datetime(2021, 12, 17, 18, 35, 56, 11182), 'benfords_result': None}}"

        # self.ingested_data_input3 = {'val': 0, 'parent_id':1}
        # self.ingested_data_input4 = {'val': -10.5, 'parent_id':1}
        self.ingested_data_input_bad1 = {'val': "string", 'parent_id':1}
        self.ingested_data_input_bad2 = {'val': 0}
        self.ingested_data_input_bad3 = {'val': 1}

        self.engine = create_engine("sqlite://", echo=False)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(self.engine)()

    def create_data(self, d):
        data = IngestedData(**d)
        self.session.add(data)
        self.session.flush()
        self.session.commit()
        return data.uid

    def create_job(self, j, session):
        job = IngestionJobs(**j)
        session.add(job)
        session.flush()
        self.session.commit()
        return job.uid

    def get_job(self, uid):
        q_res = self.session.query(IngestionJobs)
        q_res = q_res.filter_by(uid=uid)
        res = q_res.one()
        return res.to_dict(nested=True)

    def get_data(self, uid):
        q_res = self.session.query(IngestedData)
        q_res = q_res.filter_by(uid=uid)
        res = q_res.one()
        return res.to_dict(nested=True)

    def get_jobs(self):
        q_res = self.session.query(IngestionJobs).all()
        return list(q.to_dict(nested=True) for q in q_res)

    def test_serialize_mixin(self):
        self.assertEqual(IngestionJobs.relations, ['children'], 'serialize mixin may have changed')

    def test_ingestion_model(self):
        with Session(self.engine) as session:
            job = IngestionJobs(**self.ingestion_jobs_input1)
            session.add(job)
            session.flush()
            job1_uid = job.uid
            session.commit()
            q_res = session.query(IngestionJobs)
            q_res = q_res.filter_by(uid=job1_uid)
            res = q_res.one()
            resp = res.to_dict(nested=True)
            #self.assertEqual(json.dumps(resp1), self.ingestion_jobs_output1, 'Children ingested okay!')
            self.assertEqual(len(resp["children"]), 2, 'First ingestion job: Children ingested okay!')


    def test_ingestion_model2(self):
        with Session(self.engine) as session:
            job = IngestionJobs(**self.ingestion_jobs_input2)
            session.add(job)
            session.flush()
            job2_uid = job.uid
            session.commit()
            q_res = session.query(IngestionJobs)
            q_res = q_res.filter_by(uid=job2_uid)
            res = q_res.one()
            resp = res.to_dict(nested=True)
            self.assertEqual(len(resp["children"]), 2, 'Second ingestion job: children ingested okay!')

    # def test_ingested_data_model(self):
    #     data1_uid = self.create_data(self.ingested_data_input1)
    #     #data2_uid = self.create_data(self.ingested_data_input2)
    #     resp1 = self.get_data(data1_uid)
    #     #resp2 = self.get_data(data2_uid)
    #     self.assertEqual(json.dumps(resp1), self.ingested_data_output1, 'Ingested Data may have changed')

    def test_bad_data_statement_error(self):
        with self.assertRaises(StatementError):
            with Session(self.engine) as session:
                job = IngestedData(**self.ingested_data_input_bad1)
                session.add(job)
                session.flush()

    def test_bad_data_integrity_error(self):
        with Session(self.engine) as session:
            with self.assertRaises(IntegrityError):
                job = IngestedData(**self.ingested_data_input_bad2)
                session.add(job)
                session.flush()

    def tearDown(self):
        self.session.close()

if __name__ == '__main__':
    unittest.main()
