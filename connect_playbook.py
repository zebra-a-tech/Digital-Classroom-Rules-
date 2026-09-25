from flask import request

def register_playbook_connection(app):

    @app.after_request
    def connect_playbook(response):

        path = request.path

        # Only affect student Learning Centre pages
        if not path.startswith("/student/") or not path.endswith("/home"):
            return response

        try:
            html = response.get_data(as_text=True)
        except Exception:
            return response

        # Only HTML pages
        if "<html" not in html.lower():
            return response

        # Prevent duplicate button
        if "PLAYBOOK_CONNECTED" in html:
            return response

        parts = path.strip("/").split()

        # Get student ID safely
        try:
            clean = path.strip("/").split("/")
            sid = clean[1]
        except Exception:
            return response

        button = f"""
        <!-- PLAYBOOK_CONNECTED -->

        <div style="
            margin:20px 0;
            padding:20px;
            border-radius:18px;
            background:#172554;
            color:white;
            box-shadow:0 4px 15px rgba(0,0,0,.15);
        ">

            <div style="
                font-size:22px;
                font-weight:bold;
                margin-bottom:8px;
            ">
                📚 Lessons & Playbook
            </div>

            <div style="
                font-size:15px;
                line-height:1.5;
                margin-bottom:15px;
            ">
                Learn your subjects step by step with explanations,
                examples, practice questions and mastery tracking.
            </div>

            <a href="/student/{sid}/playbook"
               style="
                display:block;
                background:white;
                color:#172554;
                padding:14px;
                border-radius:12px;
                text-align:center;
                text-decoration:none;
                font-weight:bold;
                font-size:17px;
               ">
                📖 OPEN LESSONS & PLAYBOOK
            </a>

        </div>
        """

        # Insert immediately before the Learning Centre section
        markers = [
            "🚀 Learning Centre",
            "Learning Centre",
            "Open Learning Centre"
        ]

        inserted = False

        for marker in markers:
            if marker in html:
                html = html.replace(
                    marker,
                    marker + button,
                    1
                )
                inserted = True
                break

        # If the current template doesn't contain the marker,
        # insert before </body>.
        if not inserted:
            if "</body>" in html:
                html = html.replace(
                    "</body>",
                    button + "</body>",
                    1
                )
                inserted = True

        if inserted:
            response.set_data(html)

        return response


register_playbook_connection = register_playbook_connection
