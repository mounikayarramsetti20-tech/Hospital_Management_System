/* =========================================
   Hospital Management System
   Common JavaScript Utilities
   ========================================= */

function getAccessToken() {
    return localStorage.getItem("access_token");
}

function getLoggedInUser() {
    const user = localStorage.getItem("user");

    if (!user) {
        return null;
    }

    try {
        return JSON.parse(user);
    } catch (error) {
        return null;
    }
}

function getAuthHeaders() {
    const token = getAccessToken();

    const headers = {
        "Content-Type": "application/json"
    };

    if (token) {
        headers["Authorization"] = "Bearer " + token;
    }

    return headers;
}

function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    window.location.href = "/login";
}

function isLoggedIn() {
    return !!getAccessToken();
}

function requireLogin() {
    if (!isLoggedIn()) {
        window.location.href = "/login";
        return false;
    }

    return true;
}

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatDate(value) {
    if (!value) {
        return "";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}

function showError(message, elementId = "error-message") {
    const element = document.getElementById(elementId);

    if (!element) {
        alert(message);
        return;
    }

    element.textContent = message;
    element.style.display = "block";
}

function hideError(elementId = "error-message") {
    const element = document.getElementById(elementId);

    if (element) {
        element.style.display = "none";
    }
}

function showSuccess(message, elementId = "success-message") {
    const element = document.getElementById(elementId);

    if (!element) {
        alert(message);
        return;
    }

    element.textContent = message;
    element.style.display = "block";
}

function handleUnauthorized() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    window.location.href = "/login";
}

async function apiRequest(url, options = {}) {
    const token = getAccessToken();

    const headers = options.headers || {};

    if (token) {
        headers["Authorization"] = "Bearer " + token;
    }

    if (
        options.body &&
        typeof options.body === "string" &&
        !headers["Content-Type"]
    ) {
        headers["Content-Type"] = "application/json";
    }

    options.headers = headers;

    const response = await fetch(url, options);

    if (response.status === 401) {
        handleUnauthorized();
        return null;
    }

    return response;
}

function displayCurrentUser(elementId = "current-user") {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    const user = getLoggedInUser();

    if (!user) {
        element.textContent = "Not logged in";
        return;
    }

    element.textContent =
        "Logged in as: " +
        user.username +
        " (" +
        user.role +
        ")";
}

document.addEventListener("DOMContentLoaded", function () {
    const logoutButtons = document.querySelectorAll(
        "[data-action='logout']"
    );

    logoutButtons.forEach(function (button) {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            logout();
        });
    });

    displayCurrentUser();
});