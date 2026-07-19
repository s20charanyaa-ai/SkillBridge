from flask import Flask, render_template, request, redirect, session
import sqlite3


app = Flask(
    __name__,
    template_folder="../Frontend/Templates",
    static_folder="../Frontend/Static"
)

app.secret_key = "skillbridge_secret_key"


# DATABASE

def get_db():
    conn = sqlite3.connect("skillbridge.db")
    conn.row_factory = sqlite3.Row
    return conn



# HOME

@app.route("/")
def home():
    return render_template("index.html")



# REGISTER

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]


        conn = get_db()
        cursor = conn.cursor()


        # Check existing email

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()


        if user:

            conn.close()

            return """
            <h2>Email already registered!</h2>
            <p>Please login using your existing account.</p>
            <a href="/login">Go to Login</a>
            """



        cursor.execute(
            """
            INSERT INTO users(name,email,password)
            VALUES(?,?,?)
            """,
            (name,email,password)
        )


        conn.commit()
        conn.close()


        return redirect("/login")



    return render_template("register.html")




# LOGIN

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":


        email = request.form["email"]
        password = request.form["password"]


        conn = get_db()
        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=? AND password=?
            """,
            (email,password)
        )


        user = cursor.fetchone()


        conn.close()



        if user:

            session["user_id"] = user["id"]
            session["name"] = user["name"]

            return redirect("/dashboard")



        return "Invalid email or password"



    return render_template("login.html")




# DASHBOARD

@app.route("/dashboard")
def dashboard():


    if "user_id" not in session:

        return redirect("/login")



    return render_template(
        "dashboard.html",
        username=session["name"]
    )




# POST SKILL

@app.route("/postskill", methods=["GET","POST"])
def postskill():


    if "user_id" not in session:

        return redirect("/login")



    if request.method == "POST":


        skill = request.form["skill"]
        description = request.form["description"]
        category = request.form["category"]
        experience = request.form["experience"]



        conn = get_db()
        cursor = conn.cursor()



        cursor.execute(
            """
            INSERT INTO skills(
            user_id,
            skill,
            description,
            category,
            experience
            )
            VALUES(?,?,?,?,?)
            """,
            (
                session["user_id"],
                skill,
                description,
                category,
                experience
            )
        )



        conn.commit()
        conn.close()



        return redirect("/myskills")



    return render_template("postskill.html")





# MY SKILLS

@app.route("/myskills")
def myskills():


    if "user_id" not in session:

        return redirect("/login")



    conn = get_db()
    cursor = conn.cursor()



    cursor.execute(
        """
        SELECT *
        FROM skills
        WHERE user_id=?
        """,
        (session["user_id"],)
    )



    skills = cursor.fetchall()


    conn.close()



    return render_template(
        "myskills.html",
        skills=skills
    )





# FIND SKILLS
@app.route("/findskills")
def findskills():

    if "user_id" not in session:
        return redirect("/login")

    search = request.args.get("search", "")

    conn = get_db()
    cursor = conn.cursor()

    if search:

        cursor.execute(
            """
            SELECT
            skills.id,
            skills.skill,
            skills.description,
            skills.category,
            skills.experience,
            users.name

            FROM skills

            JOIN users

            ON skills.user_id = users.id

            WHERE skills.skill LIKE ?
            OR skills.category LIKE ?
            """,
            (
                "%" + search + "%",
                "%" + search + "%"
            )
        )

    else:

        cursor.execute(
            """
            SELECT
            skills.id,
            skills.skill,
            skills.description,
            skills.category,
            skills.experience,
            users.name

            FROM skills

            JOIN users

            ON skills.user_id = users.id
            """
        )


    skills = cursor.fetchall()

    conn.close()


    return render_template(
        "findskills.html",
        skills=skills
    )
# SEND REQUEST

@app.route("/request/<int:skill_id>")
def request_skill(skill_id):


    if "user_id" not in session:

        return redirect("/login")



    conn = get_db()
    cursor = conn.cursor()



    cursor.execute(
        """
        SELECT user_id
        FROM skills
        WHERE id=?
        """,
        (skill_id,)
    )



    owner = cursor.fetchone()



    cursor.execute(
        """
        INSERT INTO requests(
        sender_id,
        receiver_id,
        skill_id,
        status
        )
        VALUES(?,?,?,'Pending')
        """,
        (
            session["user_id"],
            owner["user_id"],
            skill_id
        )
    )



    conn.commit()
    conn.close()



    return "Skill Exchange Request Sent!"





# VIEW REQUESTS

@app.route("/requests")
def requests_page():


    if "user_id" not in session:

        return redirect("/login")



    conn = get_db()
    cursor = conn.cursor()



    cursor.execute(
        """
        SELECT
        requests.id,
        users.name,
        skills.skill,
        requests.status

        FROM requests

        JOIN users

        ON requests.sender_id = users.id

        JOIN skills

        ON requests.skill_id = skills.id

        WHERE requests.receiver_id=?
        """,
        (session["user_id"],)
    )



    requests = cursor.fetchall()


    conn.close()



    return render_template(
        "requests.html",
        requests=requests
    )





# ACCEPT REQUEST

@app.route("/accept/<int:req_id>")
def accept(req_id):


    conn = get_db()
    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE requests
        SET status='Accepted'
        WHERE id=?
        """,
        (req_id,)
    )


    conn.commit()
    conn.close()


    return redirect("/requests")





# REJECT REQUEST

@app.route("/reject/<int:req_id>")
def reject(req_id):


    conn = get_db()
    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE requests
        SET status='Rejected'
        WHERE id=?
        """,
        (req_id,)
    )


    conn.commit()
    conn.close()


    return redirect("/requests")





# LOGOUT

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")





if __name__ == "__main__":

    app.run()