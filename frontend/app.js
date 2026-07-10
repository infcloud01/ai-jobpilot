// frontend/app.js

const BACKEND_URL = "http://localhost:8000";
let USER_JWT_TOKEN = null;

window.onload = function () {
    // Initialize the Web Identity Verification Framework
    google.accounts.id.initialize({
        // Replace with your active Google Web Application Client ID string
        client_id: "800129858782-lhc7bfv2tti9k5rd0og5hf9962445rtg.apps.googleusercontent.com", 
        callback: handleCredentialResponse,
        auto_select: false
    });

    // Mount the structural sign-in elements
    google.accounts.id.renderButton(
        document.getElementById("google-btn"),
        { theme: "filled_blue", size: "large", text: "signin_with", shape: "rectangular" }
    );
};

function handleCredentialResponse(response) {
    USER_JWT_TOKEN = response.credential;
    
    // Parse the inner metadata parameters from the identity wrapper payload
    const base64Url = USER_JWT_TOKEN.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    const userProfile = JSON.parse(jsonPayload);

    // Apply metadata identifiers to the dashboard layout window
    document.getElementById("user-name").innerText = userProfile.name || "Google User";
    document.getElementById("user-email").innerText = userProfile.email || "";
    document.getElementById("session-text").innerText = `ID: ${userProfile.sub.substring(0, 10)}...`;

    // Swap layouts
    document.getElementById("auth-view").classList.add("hidden");
    document.getElementById("app-view").classList.remove("hidden");
}

function handleLogout() {
    USER_JWT_TOKEN = null;
    document.getElementById("app-view").classList.add("hidden");
    document.getElementById("auth-view").classList.remove("hidden");
}

async function triggerAgentRun() {
    const queryInput = document.getElementById("agent-query").value;
    const fileInput = document.getElementById("resume-file");
    const runBtn = document.getElementById("run-btn");
    const spinner = document.getElementById("loading-spinner");

    // Guardrail: Ensure file selection is checked before network transport occurs
    if (fileInput.files.length === 0) {
        alert("Please upload a valid .txt resume file format before running the analysis loop.");
        return;
    }

    // Toggle active layout states
    runBtn.disabled = true;
    runBtn.classList.add("opacity-50", "cursor-not-allowed");
    spinner.classList.remove("hidden");

    // Package runtime parameters via Multipart FormData vectors
    const formData = new FormData();
    formData.append("query", queryInput);
    formData.append("resume_file", fileInput.files[0]);

    try {
        const response = await fetch(`${BACKEND_URL}/api/agent/run`, {
            method: "POST",
            headers: {
                // Content-Type is intentionally omitted to let the browser generate multipart form boundaries
                "Authorization": `Bearer ${USER_JWT_TOKEN || "mock_local_handshake_key"}`
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server returned error status code: ${response.status}`);
        }

        const data = await response.json();
        renderDashboardResults(data);

    } catch (error) {
        alert(`API Routing Fault Detected: ${error.message}`);
        console.error("Pipeline failure trace:", error);
    } finally {
        // Restore interactive UI states
        runBtn.disabled = false;
        runBtn.classList.remove("opacity-50", "cursor-not-allowed");
        spinner.classList.add("hidden");
    }
}

function renderDashboardResults(data) {
    const score = data.metrics?.match_score || 0;
    const scoreText = document.getElementById("score-text");
    scoreText.innerText = `${score}%`;
    
    // Dynamic color coding assignment rules
    if (score >= 80) scoreText.className = "text-4xl font-black text-teal-400";
    else if (score >= 60) scoreText.className = "text-4xl font-black text-yellow-400";
    else scoreText.className = "text-4xl font-black text-rose-400";

    // Unpack Matched Core Strengths elements
    const matchedBox = document.getElementById("matched-skills");
    matchedBox.innerHTML = "";
    if (data.metrics?.matched_skills?.length > 0) {
        data.metrics.matched_skills.forEach(skill => {
            matchedBox.innerHTML += `<span class="px-2.5 py-1 rounded-md bg-teal-500/10 text-teal-300 border border-teal-500/20">${skill}</span>`;
        });
    } else {
        matchedBox.innerHTML = `<span class="text-slate-500 italic">No exact overlays cataloged.</span>`;
    }

    // Unpack Discovered Deficiencies elements
    const gapBox = document.getElementById("critical-gaps");
    gapBox.innerHTML = "";
    if (data.metrics?.critical_gaps?.length > 0) {
        data.metrics.critical_gaps.forEach(gap => {
            gapBox.innerHTML += `<span class="px-2.5 py-1 rounded-md bg-rose-500/10 text-rose-300 border border-rose-500/20">${gap}</span>`;
        });
    } else {
        gapBox.innerHTML = `<span class="text-teal-500 font-medium">0 gaps found! Perfect alignment.</span>`;
    }

    // Unpack Strategic Roadmap recommendation vectors
    const roadmapBox = document.getElementById("roadmap-list");
    roadmapBox.innerHTML = "";
    if (data.action_plan?.length > 0) {
        data.action_plan.forEach(item => {
            roadmapBox.innerHTML += `<li class="leading-relaxed"><strong class="text-blue-400">Milestone:</strong> ${item}</li>`;
        });
    } else {
        roadmapBox.innerHTML = `<li class="text-slate-500 italic">No additional actions required.</li>`;
    }
}

function devBypass() {
    console.log("🔧 Developer bypass triggered. Simulating successful authentication state...");
    
    document.getElementById("user-name").innerText = "Conrad (Dev Sandbox)";
    document.getElementById("user-email").innerText = "conrad.local@dev.ai";
    document.getElementById("session-text").innerText = "ID: local_sandbox_active";

    document.getElementById("auth-view").classList.add("hidden");
    document.getElementById("app-view").classList.remove("hidden");
}