import { useState, useRef } from "react";
import "./index.css";

function App() {
  const [symptom, setSymptom] = useState("");
  const [topology, setTopology] = useState("");
  const [commandOutput, setCommandOutput] = useState("");

  const [diagnosis, setDiagnosis] = useState(null);
  const [ruleChecker, setRuleChecker] = useState([]);

  const [reviewDecision, setReviewDecision] = useState("");
  const [reviewComment, setReviewComment] = useState("");

  const [reviewLog, setReviewLog] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const dashboardRef = useRef(null);
  const diagnosisRef = useRef(null);
  const ruleCheckerRef = useRef(null);
  const reviewRef = useRef(null);

  const scrollToSection = (ref) => {
    ref.current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  };

  const handleDiagnosis = async () => {
    if (!symptom || !topology || !commandOutput) {
      setError("Please fill in all fields.");
      return;
    }

    setLoading(true);
    setError("");

    setDiagnosis(null);
    setRuleChecker([]);
    setReviewDecision("");
    setReviewComment("");

    try {
      const response = await fetch("/diagnose", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          symptom,
          topology,
          command_output: commandOutput,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to connect to backend.");
      }

      const data = await response.json();

      setDiagnosis(data.diagnosis);
      setRuleChecker(data.rule_checker || []);

    } catch (err) {
      setError(
        "Unable to connect to NetSage AI backend. Make sure the FastAPI server is running."
      );
    }

    setLoading(false);
  };


  const saveReview = () => {
    if (!reviewDecision) {
      return;
    }

    const newReview = {
      id: Date.now(),
      symptom: symptom,
      rootCause: diagnosis?.root_cause || "Not available",
      confidence: diagnosis?.confidence || "Unknown",
      decision: reviewDecision,
      comment: reviewComment || "No comment provided",
      timestamp: new Date().toLocaleString(),
    };

    setReviewLog((previous) => [
      newReview,
      ...previous,
    ]);

    alert("Review saved successfully.");

    setReviewDecision("");
    setReviewComment("");
  };


  return (
    <div className="app">

      {/* ================= SIDEBAR ================= */}

      <aside className="sidebar">

        <div className="logo">

          <div className="logo-icon">
            N
          </div>

          <div>
            <h2>NetSage AI</h2>
            <span>Network Intelligence</span>
          </div>

        </div>


        <nav className="navigation">

          <div
            className="nav-item active"
            onClick={() => scrollToSection(dashboardRef)}
          >
            <span>⌂</span>
            Dashboard
          </div>


          <div
            className="nav-item"
            onClick={() => scrollToSection(diagnosisRef)}
          >
            <span>◈</span>
            Diagnosis
          </div>


          <div
            className="nav-item"
            onClick={() => scrollToSection(ruleCheckerRef)}
          >
            <span>✓</span>
            Rule Checker
          </div>


          <div
            className="nav-item"
            onClick={() => scrollToSection(reviewRef)}
          >
            <span>▣</span>
            Review Log
          </div>

        </nav>


        <div className="system-status">

          <div className="status-dot"></div>

          <div>
            <strong>System Online</strong>
            <span>AI Engine Active</span>
          </div>

        </div>

      </aside>


      {/* ================= MAIN ================= */}

      <main
        className="main-content"
        ref={dashboardRef}
      >

        {/* TOP BAR */}

        <header className="topbar">

          <div>

            <h1>
              Network Diagnosis Dashboard
            </h1>

            <p>
              AI-assisted Cisco network troubleshooting and diagnosis
            </p>

          </div>


          <div className="ai-status">

            <span className="status-dot"></span>

            Gemini AI Connected

          </div>

        </header>


        {/* ================= STATISTICS ================= */}

        <section className="stats-grid">

          <div className="stat-card">
            <span>Total Cases</span>
            <strong>30</strong>
            <small>Test scenarios</small>
          </div>

          <div className="stat-card">
            <span>Accepted</span>
            <strong>20</strong>
            <small>Human validated</small>
          </div>

          <div className="stat-card">
            <span>Edited</span>
            <strong>5</strong>
            <small>Human corrected</small>
          </div>

          <div className="stat-card">
            <span>Rejected</span>
            <strong>5</strong>
            <small>AI diagnosis rejected</small>
          </div>

        </section>


        {/* ================= DIAGNOSIS ================= */}

        <section
          className="diagnosis-panel"
          ref={diagnosisRef}
        >

          <div className="section-header">

            <span className="section-tag">
              NETWORK ANALYSIS
            </span>

            <h2>
              Run Diagnosis
            </h2>

            <p>
              Provide the network symptom, topology and Cisco
              command output to analyze the problem.
            </p>

          </div>


          <div className="form-grid">

            <div className="form-group">

              <label>
                Network Symptom
              </label>

              <textarea
                placeholder="Example: PC cannot reach the server"
                value={symptom}
                onChange={(e) => setSymptom(e.target.value)}
              />

            </div>


            <div className="form-group">

              <label>
                Network Topology
              </label>

              <textarea
                placeholder="Example: PC-Switch-Server"
                value={topology}
                onChange={(e) => setTopology(e.target.value)}
              />

            </div>

          </div>


          <div className="form-group">

            <label>
              Cisco Command Output
            </label>

            <textarea
              className="command-input"
              placeholder={`Example:

show interfaces status
Fa0/2 notconnect`}
              value={commandOutput}
              onChange={(e) => setCommandOutput(e.target.value)}
            />

          </div>


          {error && (
            <div className="error-message">
              {error}
            </div>
          )}


          <button
            className="diagnose-button"
            onClick={handleDiagnosis}
            disabled={loading}
          >
            {loading
              ? "Analyzing Network..."
              : "Diagnose Network"}
          </button>

        </section>


        {/* ================= AI RESULT ================= */}

        {diagnosis && (

          <section className="diagnosis-result">

            <div className="result-header">

              <span className="section-tag">
                AI ANALYSIS
              </span>

              <h2>
                Diagnosis Result
              </h2>

            </div>


            <div className="result-item">

              <div className="result-label">
                ROOT CAUSE
              </div>

              <div className="result-value">
                {diagnosis.root_cause}
              </div>

            </div>


            <div className="result-item">

              <div className="result-label">
                CONFIDENCE
              </div>

              <div className="result-value">
                {diagnosis.confidence}
              </div>

            </div>


            <div className="result-item">

              <div className="result-label">
                OSI LAYER
              </div>

              <div className="result-value">
                {diagnosis.osi_layer}
              </div>

            </div>


            <div className="result-item">

              <div className="result-label">
                EVIDENCE
              </div>

              <div className="result-value">

                <div className="evidence-box">

                  {Array.isArray(diagnosis.evidence)
                    ? diagnosis.evidence.join("\n")
                    : diagnosis.evidence}

                </div>

              </div>

            </div>


            <div className="result-item">

              <div className="result-label">
                NEXT COMMAND
              </div>

              <div className="result-value">
                {diagnosis.next_command}
              </div>

            </div>


            <div className="result-item">

              <div className="result-label">
                FIX STEPS
              </div>

              <div className="result-value">

                {Array.isArray(diagnosis.fix_steps) ? (

                  <ul className="fix-list">

                    {diagnosis.fix_steps.map(
                      (step, index) => (
                        <li key={index}>
                          {step}
                        </li>
                      )
                    )}

                  </ul>

                ) : (

                  <p>
                    {diagnosis.fix_steps}
                  </p>

                )}

              </div>

            </div>


            {/* RULE CHECKER INSIDE RESULT */}

            <div className="result-item rule-checker">

              <div className="result-label">
                RULE CHECKER
              </div>

              <div className="result-value">

                {ruleChecker.length > 0 ? (

                  <ul className="fix-list">

                    {ruleChecker.map(
                      (finding, index) => (
                        <li key={index}>
                          {finding}
                        </li>
                      )
                    )}

                  </ul>

                ) : (

                  <p>
                    No deterministic rule findings.
                  </p>

                )}

              </div>

            </div>


            {/* ================= HUMAN REVIEW ================= */}

            <div
              className="human-review"
              ref={reviewRef}
            >

              <h3>
                Human Review
              </h3>

              <p>
                Review the AI diagnosis before accepting
                or rejecting the recommendation.
              </p>


              <div className="review-actions">

                <button
                  className="review-button accept"
                  onClick={() =>
                    setReviewDecision("Accepted")
                  }
                >
                  ✓ Accept
                </button>


                <button
                  className="review-button edit"
                  onClick={() =>
                    setReviewDecision("Edited")
                  }
                >
                  ✎ Edit
                </button>


                <button
                  className="review-button reject"
                  onClick={() =>
                    setReviewDecision("Rejected")
                  }
                >
                  ✕ Reject
                </button>

              </div>


              {reviewDecision && (

                <div className="review-form">

                  <div className="review-selected">

                    Selected Decision:{" "}

                    <strong>
                      {reviewDecision}
                    </strong>

                  </div>


                  <textarea
                    placeholder="Add a review comment..."
                    value={reviewComment}
                    onChange={(e) =>
                      setReviewComment(e.target.value)
                    }
                  />


                  <button
                    className="save-review-button"
                    onClick={saveReview}
                  >
                    Save Review
                  </button>

                </div>

              )}

            </div>

          </section>

        )}


        {/* =====================================================
            RULE CHECKER PAGE / SECTION
           ===================================================== */}

        <section
          className="dashboard-section"
          ref={ruleCheckerRef}
        >

          <div className="section-header">

            <span className="section-tag">
              VALIDATION ENGINE
            </span>

            <h2>
              Rule Checker
            </h2>

            <p>
              Deterministic checks independently validate
              network evidence against known troubleshooting rules.
            </p>

          </div>


          <div className="checker-card">

            <div className="checker-status">

              <div className="checker-icon">
                ✓
              </div>

              <div>

                <strong>
                  Deterministic Validation
                </strong>

                <span>
                  Independent of Gemini AI
                </span>

              </div>

            </div>


            {ruleChecker.length > 0 ? (

              <div className="checker-findings">

                <h3>
                  Current Findings
                </h3>

                <ul>

                  {ruleChecker.map(
                    (finding, index) => (
                      <li key={index}>
                        {finding}
                      </li>
                    )
                  )}

                </ul>

              </div>

            ) : (

              <div className="empty-state">

                <strong>
                  No diagnosis available
                </strong>

                <p>
                  Run a network diagnosis to generate
                  deterministic rule findings.
                </p>

              </div>

            )}

          </div>

        </section>


        {/* =====================================================
            REVIEW LOG
           ===================================================== */}

        <section
          className="dashboard-section"
          ref={reviewRef}
        >

          <div className="section-header">

            <span className="section-tag">
              RESPONSIBLE AI
            </span>

            <h2>
              Review Log
            </h2>

            <p>
              Human decisions and comments recorded during
              the review of AI-generated diagnoses.
            </p>

          </div>


          {reviewLog.length > 0 ? (

            <div className="review-log-container">

              {reviewLog.map((review) => (

                <div
                  className="review-log-card"
                  key={review.id}
                >

                  <div className="review-log-top">

                    <span
                      className={`decision-badge ${review.decision.toLowerCase()}`}
                    >
                      {review.decision}
                    </span>

                    <span className="review-time">
                      {review.timestamp}
                    </span>

                  </div>


                  <div className="review-log-row">

                    <span>
                      Symptom
                    </span>

                    <strong>
                      {review.symptom}
                    </strong>

                  </div>


                  <div className="review-log-row">

                    <span>
                      AI Root Cause
                    </span>

                    <strong>
                      {review.rootCause}
                    </strong>

                  </div>


                  <div className="review-log-row">

                    <span>
                      Confidence
                    </span>

                    <strong>
                      {review.confidence}
                    </strong>

                  </div>


                  <div className="review-comment-display">

                    <span>
                      Reviewer Comment
                    </span>

                    <p>
                      {review.comment}
                    </p>

                  </div>

                </div>

              ))}

            </div>

          ) : (

            <div className="empty-state">

              <strong>
                No reviews recorded yet
              </strong>

              <p>
                Complete a diagnosis and submit a human
                review to create the first review-log entry.
              </p>

            </div>

          )}

        </section>

      </main>

    </div>
  );
}

export default App;