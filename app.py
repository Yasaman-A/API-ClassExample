from flask import Flask, jsonify, request
from db import get_db

app = Flask(__name__)
IDEMPOTENCY_STORE = {}



@app.get("/api")
def health():
    return (
        jsonify(
            {
                "status": "ok",
                "message": "Tools API is running",
            }
        ),
        200,
    )




@app.get("/api/v2/tools")
def list_tools_v2():
    name_query = request.args.get("name")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if name_query:
        q = f"%{name_query.strip().lower()}%"
        cursor.execute(
            """
            SELECT id, name
            FROM rest_item
            WHERE LOWER(name) LIKE %s
            ORDER BY id
            """,
            (q,),
        )
    else:
        cursor.execute(
            """
            SELECT id, name
            FROM  rest_item
            ORDER BY id
            """
        )

    tools = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"data": tools}), 200


@app.get("/api/v2/tools/<int:tool_id>")
def get_tool_v2(tool_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, name, quantity, price
        FROM rest_item
        WHERE id = %s
        """,
        (tool_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        return jsonify({"error": f"No tool found with id {tool_id}"}), 404

    row["price"] = float(row["price"])
    return jsonify({"data": row}), 200



@app.post("/api/v2/tools")
def create_tool():
    key = request.headers.get("Idempotency-Key", "").strip()
    if not key:
        return jsonify({"error": "Idempotency-Key header is required"}), 400

    if key in IDEMPOTENCY_STORE:
        return jsonify(IDEMPOTENCY_STORE[key]), 201

    body = request.get_json(silent=True) or {}
    name = body.get("name")
    quantity = body.get("quantity", 0)
    price = body.get("price", 0)

    if not name or not str(name).strip():
        return jsonify({"error": "name is required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO rest_item (name, quantity, price)
        VALUES (%s, %s, %s)
        """,
        (str(name).strip(), quantity, price),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    response_body = {
        "data": {
            "id": new_id,
            "name": str(name).strip(),
            "quantity": quantity,
            "price": price,
        }
    }
    IDEMPOTENCY_STORE[key] = response_body
    return jsonify(response_body), 201



if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000, debug=True)

