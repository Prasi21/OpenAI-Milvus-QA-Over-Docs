from flask import request, redirect, flash
from werkzeug.utils import secure_filename
import os, shutil, validators
from qa_over_docs import vector_db
from qa_over_docs import app, context, r_db, ALLOWED_EXTENSIONS, UPLOAD_FOLDER, CONTEXT_FILE, SOURCES_FILE


@app.route('/create_databases')
def create_collection():
    if not vector_db.collection_exists():
        vector_db.create_collections()
    context["collection_exists"] = True

    from qa_over_docs.relational_db import Question, Answer, Response
    r_db.create_all()

    flash("Databases successfully created", "success")
    return redirect("/")


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/include_source", methods=['GET', 'POST'])
def include_source():
    if request.method == 'POST':
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            context["sources_to_add"].append(request.form["include-url"])
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)

            context["sources_to_add"].append(filename)

    return redirect("/")

@app.route("/create_partition", methods=['GET', 'POST'])
def create_partition():
    if request.method == 'POST':
        new_partition = request.form['partition-name']
        valid = vector_db.create_partition(new_partition)
        partition_list = vector_db.retrieve_all_partition_names()
        if valid:
            context["current_partition"] = new_partition
            context["partitions"] = partition_list

    return redirect("/")

@app.route("/update_partitions", methods=['POST'])
def update_partitions():
    selected_partitions = request.get_json()
    # selected_partitions = request.form.getlist('partitions')
    print(selected_partitions)
    context["search_partitions"] = selected_partitions
    return redirect("/")



@app.route("/clear_sources_to_add")
def clear_sources_to_add():
    context["sources_to_add"] = []
    shutil.rmtree(UPLOAD_FOLDER)
    os.mkdir(UPLOAD_FOLDER)
    return redirect("/")


@app.route("/add_sources", methods=['GET', 'POST'])
def add_sources():
    if request.method == 'POST':
        if context["sources_to_add"]:
            valid_sources = []
            
            for source in context["sources_to_add"]:
                if validators.url(source) or os.path.exists(os.path.join(UPLOAD_FOLDER, source)):
                    valid_sources.append(source)
            if valid_sources:
                partition = context["current_partition"]
                vector_db.add_sources(valid_sources, partition_name=partition)
                tagged_sources = [{"source": source, "partition": partition} for source in valid_sources]
                context["sources"].extend(tagged_sources)
                clear_sources_to_add()
                flash("Successfully added sources", "success")
            else:
                flash("No valid sources provided", "warning")
        else:
            flash("No sources to add", "warning")
    return redirect("/")


@app.route("/remove_source/<int:index>")
def remove_source(index: int):
    source = context["sources"][index]
    vector_db.remove_source(source)
    flash(f"Successfully removed {source}", "primary")
    context["sources"].pop(index)
    return redirect("/")


@app.route("/delete_databases")
def delete_collection():
    vector_db.delete_collection()

    INSTANCE_DB = "instance/project.db"
    if os.path.exists(INSTANCE_DB):
        os.remove(INSTANCE_DB)

    if os.path.exists(CONTEXT_FILE):
        os.remove(CONTEXT_FILE)
    if os.path.exists(SOURCES_FILE):
        os.remove(SOURCES_FILE)

    context["collection_exists"] = False
    context["sources"] = []
    context["time_intervals"] = {}
    context["chat_items"] = []
    context["current_partition"] = "_default"
    context["partitions"] = ["_default"]
    context["search_partitions"] = ["_default"]


    flash("Databases successfully deleted", "primary")
    return redirect("/")