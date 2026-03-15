// ============================================================
// 1. CẤU HÌNH API & GLOBAL
// ============================================================
const API = {
    CATALOG: "http://localhost:8001",
    IDENTITY: "http://localhost:8003",
    BOOKING: "http://localhost:8004",
    PAYMENT: "http://localhost:8005",
    REDEMPTION: "http://localhost:8006"
};

let token = sessionStorage.getItem("token") || localStorage.getItem("token");

const BASE_PRICE = 50000;
let seatPrices = {};      
let seatLabels = {};      
let seatTypesMap = {};    
let globalConcessionsMap = {}; 

function getSeatLabel(id) {
    return seatLabels[id] || `Seat ${id}`;
}

function isTokenExpired(t) {
    if (!t) return true;
    try {
        const base64Url = t.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        const payload = JSON.parse(jsonPayload);
        return payload.exp < Date.now() / 1000;
    } catch (e) { return true; }
}

function getUserEmailFromToken() {
    if (!token) return "";
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        const payload = JSON.parse(jsonPayload);
        return payload.email || payload.sub || "";
    } catch (e) {
        return "";
    }
}

if (token && isTokenExpired(token)) {
    logout();
}

// ============================================================
// 2. AUTHENTICATION
// ============================================================

if (token && document.getElementById("user-info")) {
    document.getElementById("user-info").innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-weight:bold; color: var(--accent); margin-right: 5px;">Welcome!</span>
            <a href="history.html" class="btn" style="display: inline-flex; align-items: center; gap: 5px; background: #444; border: 1px solid #666; padding: 8px 12px; font-size: 14px;">
                <i class="fas fa-history"></i> Vé của tôi
            </a>
            <button class="btn" onclick="logout()" style="display: inline-flex; align-items: center; gap: 5px; background: #d32f2f; border: none; padding: 8px 12px; font-size: 14px;">
                <i class="fas fa-sign-out-alt"></i> Đăng xuất
            </button>
        </div>
    `;
}

function logout() {
    sessionStorage.removeItem("token");
    localStorage.removeItem("token");
    window.location.href = "index.html";
}

async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if(!email || !password) return alert("Vui lòng nhập email và mật khẩu!");

    try {
        const res = await fetch(`${API.IDENTITY}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        
        const data = await res.json();
        
        if (res.ok) {
            sessionStorage.setItem("token", data.access_token);
            window.location.href = "index.html";
        } else if (res.status === 403) {
            alert("Tài khoản chưa được kích hoạt. Vui lòng nhập mã OTP để tiếp tục.");
            window.location.href = `verify.html?email=${email}`;
        } else {
            alert("Lỗi: " + data.detail);
        }
    } catch (err) { alert("Lỗi kết nối Server"); }
}

async function register() {
    const email = document.getElementById("reg-email").value;
    const full_name = document.getElementById("reg-name").value;
    const password = document.getElementById("reg-password").value;
    const confirmPass = document.getElementById("reg-confirm-password");
    
    if(confirmPass && confirmPass.value !== password) return alert("Mật khẩu xác nhận không khớp!");
    if (!email || !full_name || !password) return alert("Vui lòng điền đầy đủ thông tin!");

    try {
        const res = await fetch(`${API.IDENTITY}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, full_name, password })
        });

        const data = await res.json();
        if (res.ok) {
            alert("Đăng ký thành công! Vui lòng kiểm tra Email để lấy mã OTP.");
            window.location.href = `verify.html?email=${email}`;
        } else {
            alert("Lỗi: " + data.detail);
        }
    } catch (err) { alert("Lỗi kết nối Server"); }
}

let resendTimer = null;
let isResending = false;

function startResendTimer() {
    const btn = document.getElementById("resend-btn");
    if (!btn) return;
    if (isResending) clearInterval(resendTimer);
    isResending = true;
    btn.classList.add("disabled");
    let timeLeft = 60;
    btn.innerText = `Gửi lại sau (${timeLeft}s)`;
    resendTimer = setInterval(() => {
        timeLeft--;
        btn.innerText = `Gửi lại sau (${timeLeft}s)`;
        if (timeLeft <= 0) {
            clearInterval(resendTimer);
            isResending = false;
            btn.classList.remove("disabled");
            btn.innerText = "Gửi lại mã";
        }
    }, 1000);
}

async function resendOTP() {
    if (isResending) return;
    const email = document.getElementById("verify-email").value;
    if (!email) return alert("Không tìm thấy email! Vui lòng kiểm tra lại đường dẫn.");
    startResendTimer();
    try {
        const res = await fetch(`${API.IDENTITY}/resend-otp`, {
            method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email })
        });
        if (res.ok) alert("Đã gửi mã OTP mới! Mã cũ đã bị hủy.");
        else alert("Lỗi: " + (await res.json()).detail);
    } catch (e) { alert("Lỗi kết nối: " + e.message); }
}

async function verifyOTP() {
    const email = document.getElementById("verify-email").value;
    const otp_code = document.getElementById("verify-code").value;
    try {
        const res = await fetch(`${API.IDENTITY}/verify`, {
            method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, otp_code })
        });
        if (res.ok) {
            alert("Tài khoản đã được xác thực! Hãy đăng nhập.");
            window.location.href = "login.html";
        } else {
            alert("Thất bại: " + (await res.json()).detail);
        }
    } catch (err) { alert("Lỗi xác thực"); }
}

async function requestOTP() { 
    const email = document.getElementById("forgot-email").value;
    if (!email) return alert("Vui lòng nhập email");
    try {
        const res = await fetch(`${API.IDENTITY}/forgot-password`, {
            method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email })
        });
        if (res.ok) {
            alert("Mã OTP đã được gửi!");
            window.location.href = `reset-password.html?email=${email}`;
        } else alert("Lỗi: " + (await res.json()).detail);
    } catch (e) { alert("Lỗi kết nối"); }
}

async function confirmReset() { 
    const email = document.getElementById("reset-email").value;
    const otp = document.getElementById("reset-otp").value;
    const newPass = document.getElementById("reset-new-pass").value;
    if (!otp || !newPass) return alert("Vui lòng nhập đủ thông tin");
    try {
        const res = await fetch(`${API.IDENTITY}/reset-password`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, otp_code: otp, new_password: newPass })
        });
        if (res.ok) {
            alert("Đổi mật khẩu thành công! Vui lòng đăng nhập lại.");
            window.location.href = "login.html";
        } else alert("Lỗi: " + (await res.json()).detail);
    } catch (e) { alert("Lỗi kết nối"); }
}

// ============================================================
// 3. HOMEPAGE LOGIC
// ============================================================

let currentTabStatus = 'NOW_SHOWING';

if (document.getElementById("movie-list")) {
    loadMovies();
    setupSearch();
    loadHero();
    setupTabs();
}

function setupTabs() {
    const tabs = document.querySelectorAll('.tabs button');
    tabs.forEach(btn => {
        btn.addEventListener('click', (e) => {
            tabs.forEach(t => t.classList.remove('active'));
            e.target.classList.add('active');
            if (e.target.innerText.includes("Sắp chiếu")) currentTabStatus = 'COMING_SOON';
            else currentTabStatus = 'NOW_SHOWING';
            const keyword = document.getElementById("search-input").value.trim();
            loadMovies(keyword);
        });
    });
}

function setupSearch() {
    const searchInput = document.getElementById("search-input");
    if (!searchInput) return;
    let timeout = null;
    searchInput.addEventListener("input", (e) => {
        const keyword = e.target.value.trim();
        clearTimeout(timeout);
        timeout = setTimeout(() => { loadMovies(keyword); }, 500);
    });
}

async function loadMovies(keyword = "") {
    try {
        let url = `${API.CATALOG}/movies?status=${currentTabStatus}`;
        if (keyword) url += `&search=${encodeURIComponent(keyword)}`;
        const res = await fetch(url);
        const movies = await res.json();
        const container = document.getElementById("movie-list");
        if (movies.length === 0) {
            const msg = currentTabStatus === 'NOW_SHOWING' ? "Hiện không có phim nào đang chiếu." : "Chưa có phim sắp chiếu.";
            container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 50px; color:#999; font-size: 18px;">${keyword ? 'Không tìm thấy phim phù hợp.' : msg}</div>`;
            return;
        }
        container.innerHTML = movies.map(m => {
            let posterSrc = m.poster_url && m.poster_url.startsWith("http") ? m.poster_url : `https://image.tmdb.org/t/p/w500/${m.poster_url}`;
            return `
            <div class="movie-card" onclick="location.href='booking.html?id=${m.movie_id}&title=${encodeURIComponent(m.title)}'">
                <div class="poster-wrapper">
                    <img src="${posterSrc}" alt="${m.title}" onerror="this.onerror=null; this.src='https://placehold.co/300x450?text=No+Image'">
                </div>
                <div class="movie-info">
                    <h3 class="movie-title">${m.title}</h3>
                    <div class="movie-meta"><span>${m.duration_minutes} mins</span><span class="rating">⭐ 8.5</span></div>
                    <button class="btn" style="width:100%; margin-top:10px">MUA VÉ</button>
                </div>
            </div>
            `;
        }).join("");
    } catch (err) { console.error(err); }
}

async function loadHero() {
    try {
        const res = await fetch(`${API.CATALOG}/movies?status=NOW_SHOWING`);
        const movies = await res.json();
        if (movies.length > 0) {
            const heroMovie = movies.find(m => m.movie_id === 1) || movies[0];
            const titleEl = document.getElementById("hero-title");
            if (titleEl) {
                titleEl.innerText = heroMovie.title;
                document.getElementById("hero-meta").innerText = `Hành động | ${heroMovie.duration_minutes} phút`;
                document.getElementById("hero-btn").onclick = () => {
                    location.href = `booking.html?id=${heroMovie.movie_id}&title=${encodeURIComponent(heroMovie.title)}`;
                };
                const heroSection = document.getElementById("hero-section");
                let bgUrl = heroMovie.poster_url;
                if (bgUrl && !bgUrl.startsWith("http")) bgUrl = `https://image.tmdb.org/t/p/original/${bgUrl}`;
                if(bgUrl) heroSection.style.backgroundImage = `url('${bgUrl}')`;
            }
        }
    } catch(e) {}
}

// ============================================================
// 4. BOOKING LOGIC
// ============================================================

let selectedSeats = [];
let cartConcessions = {}; 
let menuItems = [];
let realShowtimesData = []; 
let selectedShowtimeId = null;
let selectedCinemaName = "";
let selectedDateStr = "";
let currentScreenId = null;
let currentScreenTypeName = "";
let currentScreenTypeSurcharge = 0;
let currentScreenName = "";
let currentMovieData = null;

if (document.getElementById("step-1")) {
    initBookingPage();
}

async function loadMovieDetail(movieId) {
    try {
        const res = await fetch(`${API.CATALOG}/movies/${movieId}`);
        if (res.ok) {
            currentMovieData = await res.json();
            
            // Update movie detail section
            const posterEl = document.getElementById("movie-poster");
            const titleEl = document.getElementById("movie-title");
            const directorEl = document.getElementById("movie-director");
            const actorsEl = document.getElementById("movie-actors");
            const genreEl = document.getElementById("movie-genre");
            const releaseEl = document.getElementById("movie-release");
            const durationEl = document.getElementById("movie-duration");
            const languageEl = document.getElementById("movie-language");
            const ageEl = document.getElementById("movie-age");
            const descEl = document.getElementById("movie-description");
            
            if (posterEl) {
                let posterSrc = currentMovieData.poster_url;
                if (posterSrc && !posterSrc.startsWith("http")) {
                    posterSrc = `https://image.tmdb.org/t/p/w500/${posterSrc}`;
                }
                posterEl.src = posterSrc || "https://placehold.co/200x300?text=No+Image";
            }
            if (titleEl) titleEl.innerText = currentMovieData.title;
            if (directorEl) directorEl.innerText = currentMovieData.director || "Đang cập nhật";
            if (actorsEl) actorsEl.innerText = currentMovieData.actors || "Đang cập nhật";
            if (genreEl) genreEl.innerText = currentMovieData.genre || "Đang cập nhật";
            if (releaseEl) releaseEl.innerText = currentMovieData.release_date || "Đang cập nhật";
            if (durationEl) durationEl.innerText = `${currentMovieData.duration_minutes} phút`;
            if (languageEl) languageEl.innerText = currentMovieData.language || "Đang cập nhật";
            if (ageEl) {
                const age = currentMovieData.age_rating || "P";
                ageEl.innerText = age;
                ageEl.className = "info-value age-badge";
                if (age === "C18" || age === "18+" || age === "T18") ageEl.classList.add("age-T18");
                else if (age === "C16" || age === "16+" || age === "T16") ageEl.classList.add("age-T16");
                else if (age === "C13" || age === "13+" || age === "T13") ageEl.classList.add("age-T13");
                else ageEl.classList.add("age-P");
            }
            if (descEl) descEl.innerText = currentMovieData.description || "Chưa có mô tả.";
        }
    } catch (err) { console.error("Error loading movie detail:", err); }
}

async function initBookingPage() {
    const params = new URLSearchParams(window.location.search);
    const movieId = params.get("id");
    document.getElementById("movie-title").innerText = params.get("title") || "Movie";
    
    document.getElementById("step-1").classList.add("active");
    document.getElementById("step-2").classList.remove("active");
    document.getElementById("date-section").style.display = "none";
    document.getElementById("time-section").style.display = "none";

    // Load movie details
    loadMovieDetail(movieId);

    try {
        const res = await fetch(`${API.CATALOG}/movies/${movieId}/showtimes`);
        realShowtimesData = await res.json();
        
        const cinemaList = document.getElementById("cinema-list");
        if (realShowtimesData.length === 0) {
            cinemaList.innerHTML = "<p style='color:#999'>Chưa có lịch chiếu cho phim này.</p>";
            return;
        }
        
        const cinemasMap = {};
        realShowtimesData.forEach(st => {
            if (!cinemasMap[st.cinema_name]) cinemasMap[st.cinema_name] = [];
            cinemasMap[st.cinema_name].push(st);
        });
        
        cinemaList.innerHTML = Object.keys(cinemasMap).map(name => `
            <div class="selection-card" onclick="selectCinema('${name}')">${name}</div>
        `).join("");
    } catch (err) { console.error(err); }
}

function selectCinema(name) {
    selectedCinemaName = name;
    document.getElementById("cinema-name").innerText = name;
    document.querySelectorAll("#cinema-list .selection-card").forEach(c => c.classList.toggle("active", c.innerText.trim() === name));
    const cinemaShowtimes = realShowtimesData.filter(st => st.cinema_name === name);
    const dates = [...new Set(cinemaShowtimes.map(st => st.start_time.split('T')[0]))];
    const dateList = document.getElementById("date-list");
    dateList.innerHTML = dates.map(dateStr => {
        const d = new Date(dateStr);
        const displayDate = d.toLocaleDateString('vi-VN', { weekday: 'short', day: '2-digit', month: '2-digit' });
        return `<div class="selection-card" onclick="selectDate('${dateStr}', '${displayDate}')">${displayDate}</div>`;
    }).join("");
    document.getElementById("date-section").style.display = "block";
    document.getElementById("time-section").style.display = "none";
    document.getElementById("date-display").innerText = "--/--";
    document.getElementById("showtime-display").innerText = "--:--";
}

function selectDate(dateStr, displayDate) {
    selectedDateStr = dateStr;
    document.getElementById("date-display").innerText = displayDate;
    document.querySelectorAll("#date-list .selection-card").forEach(c => c.classList.toggle("active", c.innerText.includes(displayDate)));
    const showtimes = realShowtimesData.filter(st => st.cinema_name === selectedCinemaName && st.start_time.startsWith(dateStr));
    const timeList = document.getElementById("showtime-list");
    timeList.innerHTML = showtimes.map(st => {
        const d = new Date(st.start_time);
        const timeStr = d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        const screenTypeBadge = st.screen_type_name && st.screen_type_name !== "2D" 
            ? `<span style="font-size:10px; background:#E53935; padding:2px 5px; border-radius:3px; margin-left:5px;">${st.screen_type_name}</span>` 
            : '';
        return `<div class="selection-card" onclick="selectShowtime('${timeStr}', ${st.showtime_id}, ${st.screen_id})">${timeStr} ${screenTypeBadge}<br><small style="color:#888">${st.screen_name}</small></div>`;
    }).join("");
    document.getElementById("time-section").style.display = "block";
}

function selectShowtime(time, showtimeId, screenId) {
    selectedShowtimeId = showtimeId;
    currentScreenId = screenId;
    document.getElementById("showtime-display").innerText = time;
    
    // Get screen type info from showtime data
    const selectedShowtime = realShowtimesData.find(st => st.showtime_id === showtimeId);
    if (selectedShowtime) {
        currentScreenTypeName = selectedShowtime.screen_type_name || "2D";
        currentScreenTypeSurcharge = selectedShowtime.screen_type_surcharge || 0;
        currentScreenName = selectedShowtime.screen_name || "";
        
        // Update screen type display
        const screenTypeEl = document.getElementById("screen-type-display");
        if (screenTypeEl) {
            screenTypeEl.innerText = currentScreenTypeName;
            if (selectedShowtime.screen_type_surcharge > 0) {
                screenTypeEl.innerText += ` (+${selectedShowtime.screen_type_surcharge.toLocaleString()}đ)`;
            }
        }
    }
    
    setTimeout(() => {
        document.getElementById("step-1").classList.remove("active");
        document.getElementById("step-2").classList.add("active");
        loadSeats(); 
        loadConcessions();
    }, 300);
}

function backToStep1() {
    document.getElementById("step-2").classList.remove("active");
    document.getElementById("step-1").classList.add("active");
    selectedSeats = []; 
    cartConcessions = {};
    updateInfo();
}

async function fetchSeatTypes() {
    if (Object.keys(seatTypesMap).length > 0) return; 
    try {
        const res = await fetch(`${API.CATALOG}/seat-types`);
        if (res.ok) {
            const types = await res.json();
            types.forEach(t => {
                seatTypesMap[t.seat_type_id] = t;
            });
        }
    } catch (e) { console.error("Lỗi tải seat types:", e); }
}

async function loadSeats() {
    if (!selectedShowtimeId || !currentScreenId) return;
    
    await fetchSeatTypes();

    let bookedSeats = [];
    let seatLayout = [];
    seatPrices = {}; 
    seatLabels = {}; 

    try {
        const bookedRes = await fetch(`${API.BOOKING}/bookings/showtime/${selectedShowtimeId}/booked-seats`);
        if (bookedRes.ok) bookedSeats = await bookedRes.json();
        const layoutRes = await fetch(`${API.CATALOG}/screens/${currentScreenId}/seats`);
        if (layoutRes.ok) seatLayout = await layoutRes.json();
    } catch (err) { console.error(err); }

    const map = document.getElementById("seat-map");
    map.innerHTML = "";
    if (seatLayout.length === 0) {
        map.innerHTML = "<p style='grid-column: 1/-1; text-align: center; color: #999'>Chưa có sơ đồ ghế cho phòng này.</p>";
        return;
    }
    seatLayout.sort((a, b) => a.row_code.localeCompare(b.row_code) || a.seat_number - b.seat_number);

    // Calculate grid columns dynamically based on max seat number per row
    const maxCols = Math.max(...seatLayout.map(s => s.seat_number));
    map.style.gridTemplateColumns = `repeat(${maxCols}, 1fr)`;

    seatLayout.forEach(s => {
        const seat = document.createElement("div");
        seat.classList.add("seat");
        const label = `${s.row_code}${s.seat_number}`;
        seatLabels[s.seat_id] = label;
        seat.innerText = label;
        seat.dataset.seatId = s.seat_id;
        seat.dataset.seatTypeId = s.seat_type_id;
        seat.dataset.rowCode = s.row_code;
        seat.dataset.seatNumber = s.seat_number;
        
        let price = BASE_PRICE;
        let typeClass = "";
        let typeName = "Standard";

        if (seatTypesMap[s.seat_type_id]) {
            const t = seatTypesMap[s.seat_type_id];
            price += t.surcharge_rate;
            typeName = t.name;
            if (t.name.toLowerCase().includes('vip')) typeClass = "type-vip";
            if (t.name.toLowerCase().includes('couple')) typeClass = "type-couple";
        }

        if (!s.is_active) {
            seat.classList.add("broken");
            seat.title = "Ghế đang bảo trì";
        } 
        else if (bookedSeats.includes(s.seat_id)) {
            seat.classList.add("occupied");
            seat.title = "Ghế đã bán";
        } 
        else {
            if (typeClass) seat.classList.add(typeClass);
            seat.title = `${typeName} - ${price.toLocaleString()}đ`;
            seatPrices[s.seat_id] = price; 
            seat.onclick = () => toggleSeat(seat, s.seat_id);
        }
        map.appendChild(seat);
    });
}

function toggleSeat(el, id) {
    if (el.classList.contains("selected")) {
        el.classList.remove("selected");
        selectedSeats = selectedSeats.filter(s => s !== id);
    } else {
        el.classList.add("selected");
        selectedSeats.push(id);
    }
    updateInfo();
}

async function loadConcessions() {
    const res = await fetch(`${API.CATALOG}/concessions`);
    menuItems = await res.json();
    document.getElementById("concession-list").innerHTML = menuItems.map(i => `
        <div class="snack-card">
            <div class="snack-name">${i.name}</div>
            <div class="snack-price">${i.price.toLocaleString()} VND</div>
            <div style="display:flex; justify-content:center; gap:10px; margin-top:10px">
                <button class="btn" style="width:30px; padding:5px" onclick="updateSnack(${i.item_id}, -1)">-</button>
                <span id="qty-${i.item_id}" style="font-weight:bold">0</span>
                <button class="btn" style="width:30px; padding:5px" onclick="updateSnack(${i.item_id}, 1)">+</button>
            </div>
        </div>
    `).join("");
}

function updateSnack(id, change) {
    if (!cartConcessions[id]) cartConcessions[id] = 0;
    cartConcessions[id] += change;
    if (cartConcessions[id] < 0) cartConcessions[id] = 0;
    document.getElementById(`qty-${id}`).innerText = cartConcessions[id];
    updateInfo();
}

function updateInfo() {
    let seatTotal = 0;
    selectedSeats.forEach(id => { seatTotal += (seatPrices[id] || BASE_PRICE); });
    let snackTotal = 0;
    menuItems.forEach(i => snackTotal += (cartConcessions[i.item_id] || 0) * i.price);
    
    const countEl = document.getElementById("count");
    if (countEl) {
        countEl.innerText = selectedSeats.length;
        // Visual warning if approaching/exceeding limit
        if (selectedSeats.length > 8) {
            countEl.style.color = "#ff4757";
        } else if (selectedSeats.length >= 6) {
            countEl.style.color = "#ffa502";
        } else {
            countEl.style.color = "";
        }
    }
    document.getElementById("total").innerText = (seatTotal + snackTotal).toLocaleString();
}

async function bookAndPay() {
    if (!token) return alert("Vui lòng đăng nhập trước!");
    if (isTokenExpired(token)) {
        alert("Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại!");
        logout();
        return;
    }
    if (selectedSeats.length === 0) return alert("Chọn ít nhất 1 ghế!");
    
    // Client-side validation for better UX
    if (selectedSeats.length > 8) {
        return alert("⚠️ Bạn chỉ được đặt tối đa 8 ghế trong một lần đặt vé!");
    }
    
    const concessions = Object.keys(cartConcessions)
        .map(id => ({item_id: parseInt(id), quantity: cartConcessions[id]}))
        .filter(i => i.quantity > 0);
    
    try {
        const res = await fetch(`${API.BOOKING}/bookings`, {
            method: "POST",
            headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
            body: JSON.stringify({ showtime_id: selectedShowtimeId, seat_ids: selectedSeats, concessions })
        });
        const data = await res.json();
        
        if (res.status === 401) { alert("Phiên đăng nhập hết hạn!"); logout(); return; }
        if (!res.ok) {
            // Handle specific validation errors with user-friendly messages
            const errorMsg = data.detail || "Lỗi không xác định";
            if (errorMsg.includes("tối đa 8 ghế")) {
                alert("⚠️ Bạn chỉ được đặt tối đa 8 ghế trong một lần đặt vé!");
            } else if (errorMsg.includes("cùng loại ghế") || errorMsg.includes("same seat type")) {
                alert("⚠️ Bạn không được đặt khác loại ghế! Vui lòng chọn tất cả ghế Standard, VIP, hoặc Couple.");
            } else if (errorMsg.includes("ghế trống đơn") || errorMsg.includes("ghế trống đơn lẻ") || errorMsg.includes("single empty seat")) {
                alert("⚠️ Không được để lại ghế trống đơn lẻ giữa các ghế! Vui lòng chọn ghế liền nhau hoặc không để trống 1 ghế.");
            } else {
                alert("Lỗi đặt vé: " + errorMsg);
            }
            return;
        }
        
        let snacksStr = "";
        const snackDetails = [];
        Object.keys(cartConcessions).forEach(id => {
            if(cartConcessions[id] > 0) {
                const item = menuItems.find(i => i.item_id == id);
                snackDetails.push(`${item ? item.name : id} (x${cartConcessions[id]})`);
            }
        });
        if(snackDetails.length > 0) snacksStr = snackDetails.join(", ");
        const niceSeatsStr = selectedSeats.map(id => getSeatLabel(id)).join(", ");
        const movieTitle = document.getElementById("movie-title").innerText;
        
        // Build screen type display with surcharge
        let screenTypeDisplay = currentScreenTypeName;
        if (currentScreenTypeSurcharge > 0) {
            screenTypeDisplay += ` (+${currentScreenTypeSurcharge.toLocaleString()}đ/vé)`;
        }

        const selectedShowtime = realShowtimesData.find(st => st.showtime_id === selectedShowtimeId);
        const startTime = selectedShowtime?.start_time || "";
        window.location.href = `payment.html?id=${data.booking_id}&total=${data.total_amount}&movie=${encodeURIComponent(movieTitle)}&seats=${niceSeatsStr}&snacks=${encodeURIComponent(snacksStr)}&cinema=${encodeURIComponent(selectedCinemaName)}&screen=${encodeURIComponent(currentScreenName)}&screenType=${encodeURIComponent(screenTypeDisplay)}&showtimeId=${selectedShowtimeId}&startTime=${encodeURIComponent(startTime)}`;
    } catch (e) { alert("Lỗi đặt vé: " + e.message); }
}

// ============================================================
// 5. PAYMENT PAGE LOGIC
// ============================================================

let currentBookingId = null;
let currentAmount = 0; 

async function sendTicketEmailForCurrentBooking() {
    const p = new URLSearchParams(window.location.search);
    const userEmail = getUserEmailFromToken();
    if (!userEmail) {
        console.warn("Không lấy được email người dùng từ token.");
        return false;
    }

    let startTime = p.get("startTime") || "";
    const showtimeId = p.get("showtimeId");
    if (!startTime && showtimeId) {
        try {
            const showtimeRes = await fetch(`${API.CATALOG}/showtimes/${showtimeId}`);
            if (showtimeRes.ok) {
                const st = await showtimeRes.json();
                startTime = st.start_time || "";
            }
        } catch (e) {
            console.warn("Không tải được thông tin suất chiếu:", e);
        }
    }
    if (!startTime) startTime = new Date().toLocaleString("vi-VN");

    const seatsRaw = p.get("seats") || "";
    const seats = seatsRaw.split(",").map(s => s.trim()).filter(Boolean);
    const payload = {
        email: userEmail,
        booking_id: parseInt(currentBookingId),
        ticket_code: `CW-${currentBookingId}`,
        movie_title: p.get("movie") || "Unknown Movie",
        cinema_name: p.get("cinema") || "Unknown Cinema",
        screen_name: p.get("screen") || "Unknown Screen",
        start_time: startTime,
        seats: seats.length > 0 ? seats : ["N/A"],
        concessions_text: p.get("snacks") || "Không có",
        amount: parseInt(currentAmount) || 0,
        qr_code: `CW-${currentBookingId}-${Date.now().toString().slice(-6)}`
    };

    try {
        const res = await fetch(`${API.PAYMENT}/send-ticket`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            const errText = await res.text();
            console.error("Gửi email vé thất bại:", errText);
            return false;
        }
        return true;
    } catch (e) {
        console.error("Lỗi kết nối khi gửi email vé:", e);
        return false;
    }
}

if (document.getElementById("inv-id")) {
    loadPaymentPage();
}

function loadPaymentPage() {
    const p = new URLSearchParams(window.location.search);
    currentBookingId = p.get("id");
    currentAmount = parseFloat(p.get("total")) || 0;

    if (!currentBookingId) { 
        if(window.location.pathname.includes("payment.html")) {
             alert("Lỗi: Không tìm thấy thông tin đơn hàng!"); 
             window.location.href="index.html"; 
        }
        return;
    }

    document.getElementById("inv-id").innerText = "#" + currentBookingId;
    document.getElementById("inv-movie").innerText = p.get("movie");
    document.getElementById("inv-seats").innerText = p.get("seats");
    document.getElementById("inv-total").innerText = currentAmount.toLocaleString() + " VND";
    
    // Hiển thị rạp và loại màn hình
    const cinema = p.get("cinema");
    const screen = p.get("screen");
    const screenType = p.get("screenType");
    
    if (cinema && screen) {
        document.getElementById("inv-cinema").innerText = `${cinema} - ${screen}`;
    }
    if (screenType) {
        document.getElementById("inv-screen-type").innerText = screenType;
    }
    
    const snacks = p.get("snacks");
    if (snacks && snacks !== "") {
        const row = document.getElementById("row-snacks");
        if(row) {
            document.getElementById("inv-snacks").innerText = snacks;
            row.style.display = "flex";
        }
    }
}

async function cancelOrder() {
    if(!confirm("Bạn có chắc muốn hủy đơn hàng này không?")) return;
    try {
        const res = await fetch(`${API.BOOKING}/bookings/${currentBookingId}/cancel`, { method: "PUT" });
        if (res.ok) { 
            alert("Đã hủy đơn hàng!"); 
            window.location.href = "index.html"; 
        } else {
            alert("Lỗi khi hủy đơn.");
        }
    } catch(e) { alert("Lỗi mạng"); }
}

async function processPaymentFinal() {
    const paymentMethod = typeof selectedPaymentMethod !== 'undefined' ? selectedPaymentMethod : 'MOMO';
    
    try {
        // If mock payment is selected, validate card fields and call mock-payment endpoint
        if (paymentMethod === 'MOCK') {
            const cardNumber = document.getElementById('card-number')?.value.replace(/\s/g, '');
            const cardHolder = document.getElementById('card-holder')?.value;
            const cardExpiry = document.getElementById('card-expiry')?.value;
            const cardCvv = document.getElementById('card-cvv')?.value;
            
            if (!cardNumber || !cardHolder || !cardExpiry || !cardCvv) {
                return alert("Vui lòng nhập đầy đủ thông tin thẻ!");
            }
            
            if (cardNumber.length < 13) {
                return alert("Số thẻ không hợp lệ!");
            }
            
            const mockRes = await fetch(`${API.PAYMENT}/mock-payment`, {
                method: "POST", 
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    booking_id: parseInt(currentBookingId), 
                    amount: parseInt(currentAmount),
                    card_number: cardNumber,
                    card_holder: cardHolder,
                    card_expiry: cardExpiry,
                    card_cvv: cardCvv
                })
            });
            const mockData = await mockRes.json();
            
            if (mockRes.ok) {
                const sent = await sendTicketEmailForCurrentBooking();
                if (sent) alert("💳 Thanh toán thẻ thành công! Vé đã được gửi về email.");
                else alert("💳 Thanh toán thẻ thành công, nhưng gửi email vé thất bại. Vui lòng kiểm tra lại email hoặc liên hệ hỗ trợ.");
                window.location.href = "index.html";
            } else {
                alert("💳 Thanh toán thất bại: " + mockData.detail);
            }
            return;
        }
        
        // Default: MoMo or other payment methods
        const isFailureDemo = window.event && window.event.shiftKey;
        const res = await fetch(`${API.PAYMENT}/pay`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                booking_id: parseInt(currentBookingId), 
                amount: parseInt(currentAmount), 
                payment_method: isFailureDemo ? "FAILURE_DEMO" : "MOMO" 
            })
        });
        const data = await res.json();
        if (res.ok) { 
            const sent = await sendTicketEmailForCurrentBooking();
            if (sent) alert("Thanh toán thành công! Vé đã được gửi về email.");
            else alert("Thanh toán thành công, nhưng gửi email vé thất bại. Vui lòng kiểm tra lại email hoặc liên hệ hỗ trợ.");
            window.location.href = "index.html"; 
        }
        else alert("Thanh toán thất bại: " + data.detail);
    } catch(e) { alert("Lỗi kết nối thanh toán"); }
}

// ============================================================
// 6. HISTORY LOGIC
// ============================================================

if (document.getElementById("history-container")) {
    loadBookingHistory();
}

async function loadBookingHistory() {
    const container = document.getElementById("history-container");
    if (!token) { window.location.href = "login.html"; return; }
    if (isTokenExpired(token)) { logout(); return; }

    try {
        if (Object.keys(globalConcessionsMap).length === 0) {
            const cRes = await fetch(`${API.CATALOG}/concessions`);
            if (cRes.ok) {
                const cData = await cRes.json();
                cData.forEach(item => globalConcessionsMap[item.item_id] = item);
            }
        }

        const res = await fetch(`${API.BOOKING}/bookings/mine`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const bookings = await res.json();
        
        if (bookings.length === 0) {
            container.innerHTML = '<div class="no-data">Bạn chưa mua vé nào. <br><a href="index.html" style="color:var(--accent)">Đặt vé ngay</a></div>';
            return;
        }

        const htmls = await Promise.all(bookings.map(async b => {
            let movie = { movie_title: "Unknown", cinema_name: "Unknown", start_time: "", poster_url: "" };
            try {
                const mRes = await fetch(`${API.CATALOG}/showtimes/${b.showtime_id}`);
                if (mRes.ok) movie = await mRes.json();
            } catch(e) {}

            let statusClass = "status-pending";
            let statusText = "Chờ thanh toán";
            let actionBtn = "";
            
            if (b.status === "CONFIRMED") {
                statusClass = "status-confirmed"; 
                statusText = "Thành công";
                actionBtn = `<button class="btn" style="background:transparent; border:1px solid #FF4757; color:#FF4757; padding:5px 10px; font-size:12px; margin-top:5px;" onclick="cancelBookingFromHistory(${b.booking_id})">Hủy & Hoàn tiền</button>`;
            } else if (b.status === "CANCELLED") {
                statusClass = "status-cancelled"; 
                statusText = (b.payment_status === "REFUNDED") ? "Đã hoàn tiền" : "Đã hủy";
            }

            const d = new Date(movie.start_time);
            const niceSeats = b.seat_labels && b.seat_labels.length > 0 
                ? b.seat_labels.join(", ") 
                : b.seats.map(id => `Seat ${id}`).join(", ");
            
            const posterSrc = movie.poster_url && movie.poster_url.startsWith("http") 
                ? movie.poster_url 
                : (movie.poster_url ? `https://image.tmdb.org/t/p/w500/${movie.poster_url}` : "https://via.placeholder.com/100x140?text=Poster");
            
            let snackDisplay = "";
            if (b.concessions && b.concessions.length > 0) {
                 b.concessions.forEach(c => {
                     const item = globalConcessionsMap[c.item_id];
                     const name = item ? item.name : `Item-${c.item_id}`;
                     snackDisplay += `<div class="t-detail-sub">• ${name} (x${c.quantity})</div>`;
                 });
            }

            return `
                <div class="ticket-card">
                    <img src="${posterSrc}" class="ticket-poster">
                    <div class="ticket-info">
                        <div class="ticket-header">
                            <h3 class="t-movie">${movie.movie_title}</h3>
                            <span class="ticket-status ${statusClass}">${statusText}</span>
                        </div>
                        <div class="t-detail">Mã đơn: <b>#${b.booking_id}</b></div>
                        <div class="t-detail">Rạp: <b>${movie.cinema_name}</b></div>
                        <div class="t-detail">Suất: <b>${d.getHours()}:${String(d.getMinutes()).padStart(2,'0')} ${d.toLocaleDateString()}</b></div>
                        <div class="t-detail">Ghế: <b>${niceSeats}</b></div>
                        ${snackDisplay ? `<div class="t-detail">Bắp nước:${snackDisplay}</div>` : ""}
                        <div class="t-detail">Tổng: <b style="color:var(--accent)">${b.total_amount.toLocaleString()} VND</b></div>
                        <div style="text-align:right">${actionBtn}</div>
                    </div>
                </div>
            `;
        }));
        container.innerHTML = htmls.join("");
    } catch(e) { 
        console.error(e);
        container.innerHTML = '<div class="no-data">Lỗi tải dữ liệu.</div>'; 
    }
}

async function cancelBookingFromHistory(id) {
    if (!confirm("Bạn có chắc muốn hủy vé này? Tiền sẽ được hoàn lại.")) return;
    try {
        const res = await fetch(`${API.BOOKING}/bookings/${id}/cancel`, { method: "PUT" });
        const data = await res.json();
        if (res.ok) { 
            alert(data.message); 
            loadBookingHistory(); 
        }
        else alert("Lỗi: " + data.detail);
    } catch (e) { alert("Lỗi kết nối"); }
}