# ==========================================================
# Harvard Artifacts Streamlit App (Final Version)
# ==========================================================
import streamlit as st
import pandas as pd
import requests
import mysql.connector

# ==========================================================
# DB CONFIG
# ==========================================================
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "harvard"

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS artifact_metadata (
            id INT PRIMARY KEY,
            title TEXT,
            culture TEXT,
            `period` TEXT,
            century TEXT,
            medium TEXT,
            dimensions TEXT,
            description TEXT,
            department TEXT,
            classification TEXT,
            accessionyear INT,
            accessionmethod TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS artifact_media (
            objectid INT PRIMARY KEY,
            imagecount INT,
            mediacount INT,
            colorcount INT,
            rankk INT,
            datebegin INT,
            dateend INT,
            FOREIGN KEY (objectid) REFERENCES artifact_metadata(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS artifact_colors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            objectid INT,
            color VARCHAR(50),
            spectrum VARCHAR(50),
            hue VARCHAR(50),
            percent DECIMAL(12,10),
            css3 VARCHAR(50),
            FOREIGN KEY (objectid) REFERENCES artifact_media(objectid)
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def insert_values(artifact_metadata, artifact_media, artifact_colors):
    create_tables()
    conn = get_connection()
    cur = conn.cursor()

    q_meta = """
        INSERT IGNORE INTO artifact_metadata
        (id, title, culture, `period`, century, medium, dimensions, description,
         department, classification, accessionyear, accessionmethod)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    meta_vals = [(
        r.get('id'),
        r.get('title', ''),
        r.get('culture', ''),
        r.get('period', ''),
        r.get('century', ''),
        r.get('medium', ''),
        r.get('dimensions', ''),
        r.get('description', ''),
        r.get('department', ''),
        r.get('classification', ''),
        r.get('accessionyear'),
        r.get('accessionmethod', '')
    ) for r in artifact_metadata]

    q_media = """
        INSERT IGNORE INTO artifact_media
        (objectid, imagecount, mediacount, colorcount, rankk, datebegin, dateend)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """
    media_vals = [(
        r.get('objectid'),
        r.get('imagecount', 0),
        r.get('mediacount', 0),
        r.get('colorcount', 0),
        r.get('rankk', 0),
        r.get('datebegin'),
        r.get('dateend')
    ) for r in artifact_media]

    q_colors = """
        INSERT INTO artifact_colors
        (objectid, color, spectrum, hue, percent, css3)
        VALUES (%s,%s,%s,%s,%s,%s)
    """
    color_vals = [(
        r.get('objectid'),
        r.get('color'),
        r.get('spectrum'),
        r.get('hue'),
        r.get('percent'),
        r.get('css3')
    ) for r in artifact_colors]

    if meta_vals:
        cur.executemany(q_meta, meta_vals)
    if media_vals:
        cur.executemany(q_media, media_vals)
    if color_vals:
        cur.executemany(q_colors, color_vals)

    conn.commit()
    cur.close()
    conn.close()

# ==========================================================
# API FUNCTIONS
# ==========================================================
API_KEY = "a50a2e2e-f9f5-4654-81c0-1a92d1ec9951"

def get_valid_classifications():
    url = "https://api.harvardartmuseums.org/classification"
    params = {"apikey": API_KEY, "size": 100}
    response = requests.get(url, params=params).json()
    return [rec["name"] for rec in response["records"] if rec["objectcount"] >= 2500]

def fetch_objects(classification):
    url = "https://api.harvardartmuseums.org/object"
    objects = []
    for i in range(1, 26):  # 25 * 100 = 2500
        params = {
            "apikey": API_KEY,
            "size": 100,
            "page": i,
            "classification": classification
        }
        response = requests.get(url, params=params).json()
        objects.extend(response.get("records", []))
    return objects

def filter_fields(objs):
    metadata, media, colors = [], [], []
    for o in objs:
        metadata.append(dict(
            id=o["id"],
            title=o.get("title"),
            culture=o.get("culture"),
            period=o.get("period"),
            century=o.get("century"),
            medium=o.get("medium"),
            dimensions=o.get("dimensions"),
            description=o.get("description"),
            department=o.get("department"),
            classification=o.get("classification"),
            accessionyear=o.get("accessionyear"),
            accessionmethod=o.get("accessionmethod")
        ))
        media.append(dict(
            objectid=o["objectid"],
            imagecount=o.get("imagecount", 0),
            mediacount=o.get("mediacount", 0),
            colorcount=o.get("colorcount", 0),
            rankk=o.get("rank", 0),
            datebegin=o.get("datebegin"),
            dateend=o.get("dateend")
        ))
        for c in o.get("colors", []):
            colors.append(dict(
                objectid=o["objectid"],
                color=c.get("color"),
                spectrum=c.get("spectrum"),
                hue=c.get("hue"),
                percent=c.get("percent"),
                css3=c.get("css3")
            ))
    return metadata, media, colors

# ==========================================================
# SQL QUERIES SECTION
# ==========================================================
QUERIES = {
    # Metadata
    "1.Artifacts from 11th century (Byzantine)": "SELECT * FROM artifact_metadata WHERE century LIKE '%11th%' AND culture='Byzantine';",
    "2.Unique cultures": "SELECT DISTINCT culture FROM artifact_metadata;",
    "3.Artifacts from Archaic Period": "SELECT * FROM artifact_metadata WHERE period='Archaic';",
    "4.Artifact titles ordered by accession year (desc)": "SELECT title, accessionyear FROM artifact_metadata ORDER BY accessionyear DESC;",
    "5.Artifacts per department": "SELECT department, COUNT(*) AS total FROM artifact_metadata GROUP BY department;",

    # Media
    "6.Artifacts with >1 image": "SELECT * FROM artifact_media WHERE imagecount > 1;",
    "7.Average rank of artifacts": "SELECT AVG(rankk) AS avg_rank FROM artifact_media;",
    "8.Artifacts with colorcount > mediacount": "SELECT * FROM artifact_media WHERE colorcount > mediacount;",
    "9.Artifacts created between 1500 and 1600": "SELECT * FROM artifact_media WHERE datebegin >= 1500 AND dateend <= 1600;",
    "10.Artifacts with no media": "SELECT * FROM artifact_media WHERE mediacount=0;",

    # Colors
    "11.Distinct hues": "SELECT DISTINCT hue FROM artifact_colors;",
    "12.Top 5 most used colors": "SELECT color, COUNT(*) AS freq FROM artifact_colors GROUP BY color ORDER BY freq DESC LIMIT 5;",
    "13.Average % coverage per hue": "SELECT hue, AVG(percent) AS avg_percent FROM artifact_colors GROUP BY hue;",
    "14.Colors for artifact ID": "DYNAMIC",  # handled separately
    "15.Total number of color entries": "SELECT COUNT(*) AS total_colors FROM artifact_colors;",

    # Join Queries
    "16.Artifact titles & hues (Byzantine culture)": "SELECT m.title, c.hue FROM artifact_metadata m JOIN artifact_colors c ON m.id=c.objectid WHERE m.culture='Byzantine';",
    "17.Each artifact title with hues": "SELECT m.title, c.hue FROM artifact_metadata m JOIN artifact_colors c ON m.id=c.objectid;",
    "18.Titles, cultures, ranks where period not null": "SELECT m.title, m.culture, media.rankk FROM artifact_metadata m JOIN artifact_media media ON m.id=media.objectid WHERE m.period IS NOT NULL;",
    "19.Top 10 ranked artifacts with hue Grey": "SELECT m.title, media.rankk FROM artifact_metadata m JOIN artifact_media media ON m.id=media.objectid JOIN artifact_colors c ON m.id=c.objectid WHERE c.hue='Grey' ORDER BY media.rankk LIMIT 10;",
    "20.Artifacts per classification & avg media count": "SELECT m.classification, COUNT(*) AS total, AVG(media.mediacount) AS avg_media FROM artifact_metadata m JOIN artifact_media media ON m.id=media.objectid GROUP BY m.classification;",

    # Innovative 5
    "21.Most common mediums": "SELECT medium, COUNT(*) AS freq FROM artifact_metadata WHERE medium IS NOT NULL GROUP BY medium ORDER BY freq DESC LIMIT 5;",
    "22.Departments with artifacts spanning >500 years": "SELECT department, MIN(datebegin) AS earliest, MAX(dateend) AS latest, (MAX(dateend) - MIN(datebegin)) AS span_years FROM artifact_media m JOIN artifact_metadata meta ON m.objectid = meta.id WHERE m.datebegin IS NOT NULL AND m.dateend IS NOT NULL GROUP BY department HAVING span_years > 500;",
    "23.Top 10 longest artifact titles": "SELECT id, title, LENGTH(title) AS title_length FROM artifact_metadata WHERE title IS NOT NULL ORDER BY title_length DESC LIMIT 10;",
    "24.Average number of colors per artifact": "SELECT AVG(color_count) AS avg_colors_per_artifact FROM (SELECT objectid, COUNT(*) AS color_count FROM artifact_colors GROUP BY objectid) sub;",
    "25.Artifacts with missing title or culture": "SELECT * FROM artifact_metadata WHERE title IS NULL OR culture IS NULL;"
}

# ==========================================================
# STREAMLIT APP
# ==========================================================
st.set_page_config(page_title="Harvard’s Artifacts Collection", layout="wide")
# st.title("🎨🏛️ Harvard’s Artifacts Collection")
st.markdown(
    "<h1 style='text-align: center;'>🎨🏛️ Harvard’s Artifacts Collection</h1>",
    unsafe_allow_html=True
)

page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://t4.ftcdn.net/jpg/06/41/88/51/240_F_641885187_pGulXn8nOS2kjIBPnCUo5QkftVlUbfTP.jpg"); /* Example museum photo */
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0); /* Make header transparent */
}

h1 {
    text-align: center;
    color: white; /* Change text color for better contrast */
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

valid_classes = get_valid_classifications()
classification = st.selectbox("Choose a classification", valid_classes)

col1, col2, col3 = st.columns([2, 2, 2])

# ----------------------------
# 1. Collect Data
# ----------------------------
if col1.button("📥 Collect Data"):
    with st.spinner(f"Fetching 2500 objects for {classification}..."):
        objects = fetch_objects(classification)
        metadata, media, colors = filter_fields(objects)
        st.session_state["metadata"] = metadata
        st.session_state["media"] = media
        st.session_state["colors"] = colors
    st.success(f"✅ Collected {len(metadata)} metadata, {len(media)} media, and {len(colors)} color records for {classification}")
# ----------------------------
# 2. Show Data
# ----------------------------
if col2.button("📊 Show Data"):
    if "metadata" in st.session_state:
        meta_len = len(st.session_state["metadata"])
        media_len = len(st.session_state["media"])
        colors_len = len(st.session_state["colors"])

        st.subheader("📊 Data Counts")
        st.write(f"**Metadata records:** {meta_len}")
        st.write(f"**Media records:** {media_len}")
        st.write(f"**Color records:** {colors_len}")

        st.subheader("📑 Artifact Metadata")
        st.dataframe(pd.DataFrame(st.session_state["metadata"]), use_container_width=True)

        st.subheader("🖼️ Artifact Media")
        st.dataframe(pd.DataFrame(st.session_state["media"]), use_container_width=True)

        st.subheader("🎨 Artifact Colors")
        st.dataframe(pd.DataFrame(st.session_state["colors"]), use_container_width=True)
    else:
        st.warning("⚠️ Collect data first.")


# ----------------------------
# 3. Insert into SQL
# ----------------------------
if col3.button("💾 Insert into SQL"):
    if "metadata" in st.session_state:
        with st.spinner("Inserting records into MySQL..."):
            insert_values(
                st.session_state["metadata"],
                st.session_state["media"],
                st.session_state["colors"]
            )
        st.success("✅ Data inserted into MySQL.")
    else:
        st.warning("⚠️ Collect data first.")

# ----------------------------
# 4. SQL Queries Section
# ----------------------------
st.header("🔎 SQL Queries")

query_name = st.selectbox("Choose a query to run", list(QUERIES.keys()))

artifact_id = None
if query_name == "Colors for artifact ID":
    artifact_id = st.text_input("Enter Artifact ID:", "")

if st.button("▶️ Run Query"):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if query_name == "Colors for artifact ID" and artifact_id.strip():
        cur.execute("SELECT * FROM artifact_colors WHERE objectid=%s;", (artifact_id,))
    else:
        cur.execute(QUERIES[query_name])

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("ℹ️ No results found.")
                