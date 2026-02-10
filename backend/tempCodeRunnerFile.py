

    recs.append("Increase tree plantation in identified green clusters")
    return jsonify(recs)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
