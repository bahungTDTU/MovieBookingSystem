# 🎬 CineWorld - Microservices Movie Booking System

A comprehensive online movie booking system built on a Microservices architecture, featuring payment integration, E-Ticket delivery via Email, and a cinema management dashboard.

## 📖 Introduction

CineWorld is a complete solution for cinema chains, consisting of:

-   **Web Client**: Allows customers to browse movies, book tickets, select seats, purchase concessions, and pay online.
-   **Admin Dashboard**: Empowers managers to schedule showtimes, manage movies, configure seat layouts, and view revenue reports.
-   **Staff Scanner**: A tool for ticket checkers to scan barcodes and check customers into the theater.
-   **Background System**: An automated system for holding seats and cancelling expired pending bookings.

## ✨ Key Features

### 👤 For Customers

-   **Live Search**: Instant movie search bar in the header.
-   **Smart Booking**: Intuitive flow: Cinema → Date → Time → Seat.
-   **Seat Selection**: Visual seat map showing VIP/Couple seats and occupied status.
-   **Concessions**: Add popcorn/drinks to the order with auto-calculated totals.
-   **E-Ticket**: Receive electronic tickets via Email with a scannable Barcode.
-   **My Tickets**: View booking history with color-coded statuses.
-   **Refund**: Self-service cancellation and refund for unused tickets.

### 🛠 For Admins

-   **Dashboard**: Real-time charts for revenue and ticket sales.
-   **Manage Movies**: Add new movies and update their status (Coming Soon/Now Showing/Ended).
-   **Seat Layout**: Visual configuration for seat types (VIP, Standard) and maintenance locks.
-   **Batch Schedule**: Schedule showtimes for multiple screens at once.

### 🎫 For Staff

-   **Ticket Scanner**: Verify booking barcodes.
-   **Check-in**: Validate entry and prevent double usage.
-   **Physical Print**: Print thermal tickets for customers on demand.

## 🏗️ System Architecture (Microservices)

The system is divided into 7 independent services communicating via REST APIs.

| Service Name      | Port | Main Responsibility                                       |
| ----------------- | ---- | --------------------------------------------------------- |
| Identity Service  | 8003 | Register, Login (JWT), OTP Verification, Password Reset.  |
| Catalog Service   | 8001 | Manage Movies, Cinemas, Screens, Showtimes, Concessions.  |
| Booking Service   | 8004 | Handle bookings, seat holding, pricing, order management. |
|                   |      | Send Emails (SMTP)                                        |
| Payment Service   | 8005 | Mock payment processing, Refund handling.                 |
| OTP Service       | 8002 | Generate OTPs, Generate Barcodes.     |
| Redemption Service| 8006 | Scan tickets, validate ticket status (Check-in).          |
| Management Service| 8007 | Protected APIs for Admin (Stats, CRUD Operations).        |
| System Scheduler  | N/A  | Background robot to auto-cancel PENDING orders.           |
| Frontend (Nginx)  | 3000 | User Interface (Static Web).                              |

## 🚀 Getting Started

### Prerequisites

-   Docker Desktop installed and running.

### Step 1: Configure Email (Crucial)

Open `docker-compose.yml`, find `otp_service`, and update your Gmail credentials to enable email sending. **Note**: Use a [Google App Password](https://support.google.com/accounts/answer/185833), not your regular login password.

```yaml
    otp_service:
        environment:
            SMTP_EMAIL: "your_email@gmail.com"
            SMTP_PASSWORD: "your_16_digit_app_password"
```

### Step 2: Start the System

Open a terminal in the project's root directory and run:

```bash
docker-compose up -d --build
```

Wait 1-2 minutes for Docker to build images and start the containers. The system automatically runs `database/init.sql` on the first launch to seed data.
If the container is now run, just try again in a few minute.

### Step 3: Access the Application

-   **Home Page (Customer)**: [http://localhost:3000](http://localhost:3000)
-   **Admin Dashboard**: [http://localhost:3000/admin.html](http://localhost:3000/admin.html)
-   **Staff Scanner**: [http://localhost:3000/scanner.html](http://localhost:3000/scanner.html)
-   **Database Manager (Adminer)**: [http://localhost:8080](http://localhost:8080)
        -   **User**: `root`, **Password**: `rootpassword`, **Database**: `movie_booking_db`

## 🔐 Demo Accounts & Usage

### Creating Admin/Staff Accounts

1.  Register a new account at [http://localhost:3000/register.html](http://localhost:3000/register.html).
2.  Go to Adminer at [http://localhost:8080](http://localhost:8080) and log in.
3.  Run the following SQL query to assign a role. Replace the email with your registered email.
        -   **For Admin**: `UPDATE users SET role = 'ADMIN' WHERE email = 'your_registered_email';`
        -   **For Staff**: `UPDATE users SET role = 'TICKET_CHECKER' WHERE email = 'your_registered_email';`
4.  Log in at the Admin Dashboard or Staff Scanner page.

### API Testing with Swagger

#### How to Get an Access Token

1.  Go to the Identity Service docs: [http://localhost:8003/docs](http://localhost:8003/docs).
2.  Find the `POST /login` endpoint and click **Try it out**.
3.  Enter your credentials in the JSON body and click **Execute**.
4.  Copy the `access_token` from the response.

#### How to Use the Token

1.  Go to the Swagger UI of the service you want to test (e.g., Management Service: [http://localhost:8007/docs](http://localhost:8007/docs)).
2.  Click the **Authorize** button (green lock icon).
3.  Paste your token into the `Value` box and click **Authorize**.
4.  You can now test protected API endpoints.

### 📚 API Documentation (Swagger UI)

-   **Catalog**: [http://localhost:8001/docs](http://localhost:8001/docs)
-   **OTP**: [http://localhost:8002/docs](http://localhost:8002/docs)
-   **Identity**: [http://localhost:8003/docs](http://localhost:8003/docs)
-   **Booking**: [http://localhost:8004/docs](http://localhost:8004/docs)
-   **Payment**: [http://localhost:8005/docs](http://localhost:8005/docs)
-   **Redemption**: [http://localhost:8006/docs](http://localhost:8006/docs)
-   **Management**: [http://localhost:8007/docs](http://localhost:8007/docs)

## 🛠️ Troubleshooting

1.  **Email not sending?**
        -   Verify `SMTP_EMAIL` and `SMTP_PASSWORD` in `docker-compose.yml`.
        -   Ensure you are using a Google App Password.
2.  **Error 500 when booking?**
        -   This is often due to inconsistent data. Reset the database by running:
                ```bash
                docker-compose down -v
                docker-compose up -d --build
                ```
3.  **Frontend not updating?**
        -   Press `Ctrl + F5` (or `Cmd + Shift + R`) in your browser to perform a hard refresh and clear the cache.

---
Developed by Nguyen Ba Hung, Chau Pham Tuan Kiet, Nguyen Bao Long - Final Project SOA 2025
