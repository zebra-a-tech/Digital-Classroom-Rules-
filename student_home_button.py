from flask import request

def register_playbook_button(app):

    @app.after_request
    def add_playbook_button(response):

        path = request.path

        # Only add the button to the student's Learning Centre
        if "/student/" not in path or not path.endswith("/home"):
            return response

        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type:
            return response

        html = response.get_data(as_text=True)

        # Don't add it twice
        if "OPEN_PLAYBOOK_BUTTON" in html:
            return response

        parts = path.strip("/").split("/")

        try:
            sid_index = parts.index("student") + 1
            sid = int(parts[sid_index])
        except Exception:
            return response

        button = f"""
        <!-- OPEN_PLAYBOOK_BUTTON -->
        <div style="
            margin:18px 0;
            background:linear-gradient(135deg,#172554,#2563eb);
            padding:18px;
            border-radius:18px;
            box-shadow:0 4px 14px rgba(0,0,0,.15);
        ">
            <div style="
                color:white;
                font-size:21px;
                font-weight:bold;
                margin-bottom:7px;
            ">
                📚 Lessons & Playbook
            </div>

            <div style="
                color:#e5e7eb;
                font-size:14px;
                line-height:1.5;
                margin-bottom:13px;
            ">
                Learn step by step, study examples, practise questions
                and build your mastery.
            </div>

            <a href="/student/{sid}/playbook"
               style="
                display:block;
                text-align:center;
                text-decoration:none;
                background:white;
                color:#172554;
                padding:13px;
                border-radius:11px;
                font-weight:bold;
                font-size:16px;
               ">
                📖 Open Lessons
            </a>
        </div>
        """

        if "</body>" in html:
            html = html.replace("</body>", button + "\n</body>", 1)
            response.set_data(html)

        return response


register_student_home_button = register_playbook_button
