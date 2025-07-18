from httpx import AsyncClient

from app.dto.request.book_req import BookBulkUpdateNameReq
from app.model.book import Book
from app.repository.book_repository import BookRepository
from app.repository.params.book_repository_param import BookCreate, BookFilter
from core.mysql.database.app.app_session import AppSession
from core.status_enum import StatusEnum
from core.util.datetime import DateTime


async def test_get_book(client: AsyncClient):
    response = await client.post('/api/book/get', json={'id': 1})
    print(response.json())
    assert response.status_code == 200
    assert response.json()['code'] == StatusEnum.success.value
    assert response.json()['data'] is not None


async def test_list_book(client: AsyncClient):
    response = await client.post('/api/book/list', json={'page': 1, 'limit': 1})
    assert response.status_code == 200
    assert response.json()['code'] == StatusEnum.success.value
    assert isinstance(response.json()['data']['data'], list)
    assert response.json()['data']['total'] >= len(response.json()['data']['data'])


async def test_book_repository_create(app_session: AppSession):
    repository = BookRepository()
    book = await repository.find(session=app_session, pk=1)
    assert book is not None

    async with app_session.transaction():
        book.name = 'test' + DateTime.datetime()
        book1 = await repository.create(app_session, BookCreate(name='test'))
        book2 = await repository.create(app_session, BookCreate(name='test'))
        assert book2.id - book1.id == 1

    async with app_session.transaction():
        book.name = 'test1' + DateTime.datetime()

    book.name = 'test2' + DateTime.datetime()
    await app_session.commit()

    await repository.update(app_session, book, {'name': 'test3' + DateTime.datetime()})
    await app_session.commit()


async def test_book_repository_query(app_session: AppSession):
    repository = BookRepository()
    book_filter = BookFilter(name_like='test')
    book_filter.order_by(Book.created_at.desc())
    book = await repository.get_one(app_session, book_filter)
    assert isinstance(book, Book)


async def test_bulk_update_name(client: AsyncClient):
    param = [
        BookBulkUpdateNameReq(id=108, name='test' + DateTime.datetime()).model_dump(),
        BookBulkUpdateNameReq(id=109, name='test' + DateTime.datetime()).model_dump(),
    ]
    response = await client.post('/api/book/bulk_update_name', json={'books': param})
    print(response.json())
    assert response.status_code == 200
    assert response.json()['code'] == StatusEnum.success.value
