from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from LAMA.auth import login_required
from LAMA.db import get_db

from isbnlib.dev._exceptions import NoDataForSelectorError

import isbnlib

bp = Blueprint('book', __name__)


@bp.route('/')
def index():
    return render_template('auth/index.html')

@bp.route('/home')
@login_required
def home():
    return render_template('book/home.html')

@bp.route('/newbook', methods=('GET', 'POST'))
@login_required
def newbook():
    if request.method == 'POST':
        barcode = str(request.form['barcode'])
        isbn = isbnlib.canonical(request.form['isbn'])
        # invoice = request.form['invoice']
        error = None
        author = None
        lang = None
        publisher = None
        title = None
        publYear = None
        db = get_db()

        # Ensure barcode has not already been inserted to Database
        if db.execute(
            'SELECT id FROM new_book WHERE barcode = ?', (barcode,)
        ).fetchone() is not None:
            error = 'Barcode {} is already captured.'.format(barcode)

        # Checks correct barcode length    
        elif int(len(barcode)) != 24:
            error = '{} is an incorrect length.'.format(barcode)
            
        # ISBN Validation
        elif isbnlib.is_isbn10(isbn) is not True:
            if isbnlib.is_isbn13(isbn) is not True:
                error = f'{isbn} is not a valid ISBN' 
        
        if error is not None:
            flash(error)
        else:
            try:
                book_lib = (isbnlib.meta(isbn, service='goob', cache='default'))
                # Display meta data to user.
                flash(book_lib)

                # Assign meta dictionary values to variables for insertion to DB.
                author = str(book_lib['Authors'])
                lang = book_lib['Language']
                publisher = book_lib['Publisher']
                title = book_lib['Title']
                publYear = book_lib['Year']
            
            # Catch exception error for book that was not found on search. 
            except NoDataForSelectorError:
                flash("Book recorded: Author, Title not found.")
                pass
            # execute query and insert data
            db.execute(
                'INSERT INTO new_book (barcode, isbn, author_id, author, lang, publisher, title, publYear)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (barcode, isbn, g.user['id'], author, lang, publisher, title, publYear)
            )
            db.commit()
            return redirect(url_for('book.newbook'))
    
    return render_template('book/newbook.html')

@bp.route('/selectLib', methods=('GET', 'POST'))
@login_required
def selectLib():

    return render_template('book/selectLib.html')


@bp.route('/quality', methods=('GET', 'POST'))
@login_required
def quality():
    if request.method == 'POST':
        barcode = str(request.form['barcode'])
        db = get_db()
        qualitySearch = db.execute(
            'SELECT * FROM new_book WHERE barcode = ?', (barcode,)
        ).fetchone()

        if db.execute(
            'SELECT id FROM new_book WHERE barcode = ?', (barcode,)
        ).fetchone() is None:
            flash('Barcode {} not found, please ensure the book has been catalogued'.format(barcode))
        else:
            lsitQualitySearch = list(qualitySearch)
            newList = str(f"Barcode: {lsitQualitySearch[3:4]} ISBN: {lsitQualitySearch[4:5]} AUTHOR: {lsitQualitySearch[5:6]} TITLE: {lsitQualitySearch[8:9]}")
            flash(newList.replace("[","").replace("]",""))
        return redirect(url_for('book.quality'))

    return render_template('book/quality.html')


@bp.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    if request.method == 'POST':
        barcode = str(request.form['barcode'])
        db = get_db()
        barcodeSearch = db.execute(
            'SELECT * FROM new_book WHERE barcode = ?', (barcode,)
        ).fetchone()

        if db.execute(
            'SELECT id FROM new_book WHERE barcode = ?', (barcode,)
        ).fetchone() is None:
            flash('Barcode {} not found'.format(barcode))
        else:
            listBarcodeResult = list(barcodeSearch)
            flash(listBarcodeResult[3:])

        return redirect(url_for('book.search'))

    return render_template('book/search.html')

@bp.route('/converter', methods=('GET', 'POST'))
@login_required
def converter():
    if request.method == 'POST':
        ISBN_13 = isbnlib.canonical(request.form['ISBN-13'])
        ISBN_10 = isbnlib.canonical(request.form['ISBN-10'])

        #converts ISBNS
        flash(isbnlib.to_isbn13(ISBN_10))
        flash(isbnlib.to_isbn10(ISBN_13))

        return redirect(url_for('book.converter'))

    return render_template('book/converter.html')