from typing import Type, Union

import pydantic
from flask import Flask, jsonify, request
from flask.views import MethodView

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (Column, DateTime, Integer, String, create_engine, func)

app = Flask("app")

#
ADS_DSN = "postgresql://user:12345@127.0.0.1:5432/ads_base"
engine = create_engine(ADS_DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class AdModel(Base):
    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    owner = Column(String(200), index=True, nullable=False)


Base.metadata.create_all(engine)


class HTTPError(Exception):
    def __init__(self, status_code: int, message: Union[str, list, dict]):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HTTPError)
def handle_invalid_usage(error: HTTPError):
    response = jsonify({'status': 'error', 'message': error.message})
    response.status_code = error.status_code
    return response


class CreateAdModel(pydantic.BaseModel):
    title: str
    description: str
    owner: str

    @pydantic.validator("title")
    def min_max_length(cls, value: str):
        if 5 > len(value) > 50:
            raise ValueError('Заголовок должен содержать от 5 до 50 символов')
        return value


def validate(data_to_validate: dict, validation_class: Type[CreateAdModel]):
    try:
        return validation_class(**data_to_validate).dict()
    except pydantic.ValidationError as er:
        raise HTTPError(400, er.errors())


class AdView(MethodView):
    def get(self, id_ad: int):
        with Session() as session:
            ad = session.query(AdModel).filter(AdModel.id == id_ad).first()
            if id_ad != AdModel.id:
                raise HTTPError(400, 'error')
            return jsonify({
                'id': ad.id,
                'title': ad.title,
                'created_at': ad.created_at,
                'description': ad.description,
                'owner': ad.owner,
            })

    def post(self):
        json_data = dict(request.json)

        with Session() as session:
            try:
                ads = AdModel(**validate(json_data, CreateAdModel))
                session.add(ads)
                session.commit()

            except pydantic.ValidationError as er:
                raise HTTPError(400, er.errors())
            return jsonify({
                'status': 'ok',
                'id': ads.id,
                'owner': ads.owner,
            })

    def delete(self, id_ad: str):
        try:
            with Session() as session:
                ad = session.query(AdModel).filter(AdModel.id == id_ad).first()
                session.delete(ad)
                session.commit()
                return jsonify({
                    'status': 'success'
                })
        except pydantic.ValidationError as er:
            raise HTTPError(400, er.errors())


app.add_url_rule('/advert/<int:id_ad>/', view_func=AdView.as_view('advertisements_delete'),
                 methods=['DELETE', 'GET'])
app.add_url_rule('/advert/', view_func=AdView.as_view('advertisements_create'), methods=['POST'])

app.run()
