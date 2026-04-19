-- ============================================================
-- XML / XPath EXPERIMENT — EV Battery Health Monitoring System
-- ADBMS Topic: Semi-structured data storage & querying in PostgreSQL
-- ============================================================

-- PostgreSQL has native XML type + XPath + XMLTABLE support
-- This stores battery reports as XML and queries them with XPath

-- 1. Create XML-based report table


CREATE TABLE battery_xml_reports (
    report_id   SERIAL PRIMARY KEY,
    vehicle_id  INT REFERENCES vehicles(vehicle_id),
    report_date DATE DEFAULT CURRENT_DATE,
    report_data XML   -- stores structured report as XML
);


-- ============================================================
-- 2. Insert sample XML documents
-- ============================================================

INSERT INTO battery_xml_reports (vehicle_id, report_data) VALUES
(1, XMLPARSE(DOCUMENT '
<battery_report>
  <vehicle_number>MH12AB1111</vehicle_number>
  <model>Tata Nexon EV</model>
  <owner>Amit Shah</owner>
  <readings>
    <reading>
      <timestamp>2025-01-15T10:00:00</timestamp>
      <voltage>48.5</voltage>
      <current>12.3</current>
      <temperature>34.6</temperature>
      <soc>82</soc>
    </reading>
    <reading>
      <timestamp>2025-02-10T09:00:00</timestamp>
      <voltage>47.8</voltage>
      <current>11.9</current>
      <temperature>35.2</temperature>
      <soc>79</soc>
    </reading>
  </readings>
  <health>
    <soh>93</soh>
    <degradation>7</degradation>
    <status>Good</status>
  </health>
</battery_report>
')),
(2, XMLPARSE(DOCUMENT '
<battery_report>
  <vehicle_number>KA01CD2222</vehicle_number>
  <model>MG ZS EV</model>
  <owner>Riya Verma</owner>
  <readings>
    <reading>
      <timestamp>2025-01-15T10:05:00</timestamp>
      <voltage>47.9</voltage>
      <current>11.8</current>
      <temperature>36.1</temperature>
      <soc>78</soc>
    </reading>
  </readings>
  <health>
    <soh>86</soh>
    <degradation>14</degradation>
    <status>Fair</status>
  </health>
</battery_report>
')),
(5, XMLPARSE(DOCUMENT '
<battery_report>
  <vehicle_number>DL08JK5555</vehicle_number>
  <model>Hyundai Kona EV</model>
  <owner>Karan Singh</owner>
  <readings>
    <reading>
      <timestamp>2025-01-15T10:20:00</timestamp>
      <voltage>50.1</voltage>
      <current>13.4</current>
      <temperature>32.6</temperature>
      <soc>90</soc>
    </reading>
  </readings>
  <health>
    <soh>95</soh>
    <degradation>5</degradation>
    <status>Excellent</status>
  </health>
</battery_report>
'));


-- ============================================================
-- 3. XPath Queries
-- ============================================================

-- Extract owner name from XML
SELECT
    report_id,
    (xpath('//owner/text()', report_data))[1]::TEXT AS owner_name,
    (xpath('//health/soh/text()', report_data))[1]::TEXT AS soh,
    (xpath('//health/status/text()', report_data))[1]::TEXT AS status
FROM battery_xml_reports;


-- Extract all voltage readings using xpath
SELECT
    report_id,
    unnest(xpath('//reading/voltage/text()', report_data))::TEXT::FLOAT AS voltage_reading
FROM battery_xml_reports;


-- Filter: vehicles with SOH above 90 using XPath
SELECT
    report_id,
    (xpath('//vehicle_number/text()', report_data))[1]::TEXT AS vehicle,
    (xpath('//health/soh/text()', report_data))[1]::TEXT::FLOAT AS soh
FROM battery_xml_reports
WHERE ((xpath('//health/soh/text()', report_data))[1]::TEXT)::FLOAT > 90;


-- ============================================================
-- 4. XMLTABLE — relational output from XML (advanced)
-- ============================================================

-- Flatten readings from XML into rows
SELECT
    r.report_id,
    (xpath('//vehicle_number/text()', r.report_data))[1]::TEXT AS vehicle,
    x.ts,
    x.voltage,
    x.temperature,
    x.soc
FROM battery_xml_reports r,
XMLTABLE('//readings/reading' PASSING r.report_data
    COLUMNS
        ts          TEXT    PATH 'timestamp',
        voltage     FLOAT   PATH 'voltage',
        temperature FLOAT   PATH 'temperature',
        soc         FLOAT   PATH 'soc'
) AS x;


-- ============================================================
-- 5. Generate XML from relational data (XML export)
-- ============================================================

-- Export battery_health as XML
SELECT XMLELEMENT(
    NAME "battery_report",
    XMLFOREST(
        v.vehicle_number AS "vehicle_number",
        v.model          AS "model",
        bh.soh           AS "soh",
        bh.degradation   AS "degradation",
        bh.record_date   AS "record_date"
    )
)
FROM battery_health bh
JOIN vehicles v ON bh.vehicle_id = v.vehicle_id;


-- ============================================================
-- Summary of ADBMS Concepts Demonstrated
-- ============================================================
-- 1. XML as a column type (semi-structured data in RDBMS)
-- 2. XMLPARSE — inserting XML documents
-- 3. xpath() — querying nested XML nodes
-- 4. XMLTABLE — shredding XML into relational rows
-- 5. XMLELEMENT / XMLFOREST — generating XML from SQL
-- 6. Combining XPath filtering with SQL WHERE clause
-- ============================================================