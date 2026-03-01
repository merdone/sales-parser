# Biedronka Promotions Frontend (React)

A modern React frontend for the Biedronka promotions parser, built with Vite.

## 🚀 Setup

```bash
cd frontend
npm install
```

## 📦 Scripts

### Development
```bash
npm run dev
```
Starts the dev server at `http://localhost:5173` with hot reload.

### Production build
```bash
npm run build
```
Creates an optimized build in `dist/`.

### Preview production build
```bash
npm run preview
```

### Lint
```bash
npm run lint
```

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── CategoryDropdown.jsx
│   │   ├── ProductGrid.jsx
│   │   ├── SortButtons.jsx
│   │   ├── CartModal.jsx
│   │   └── *.css
│   ├── hooks/               # Custom React hooks
│   │   ├── useCart.js        # Cart state
│   │   └── useProducts.js    # Product data
│   ├── App.jsx               # Root component
│   ├── App.css
│   ├── index.css             # Global styles
│   └── main.jsx              # Entry point
├── index.html
├── vite.config.js            # Vite configuration
└── package.json
```

## 🔧 Configuration

### API proxy
In `vite.config.js`, requests to `/api/*` are proxied to `http://localhost:8000/api/*`.

Make sure the backend is running on port 8000.

## 🎨 Features

- ✅ Category filtering
- ✅ Sorting by price and name
- ✅ Cart stored in localStorage
- ✅ Responsive layout
- ✅ Hot reload in development
- ✅ Optimized production build

## 🧭 Pages

- `Home` (`/`) — main promotions grid with category/store/promotion filters, search, and sorting.
- `Leaflet` (`/magazine`) — booklet-style viewer for original leaflet pages with zoom and thumbnails.

When you click **View original page** on a product card, the app opens the leaflet spread.
Inside the leaflet viewer you can click a product area to add it to the cart (mask-based click detection).

## 💾 Local storage
The cart is stored in the browser `localStorage` under the `cart` key.

## 🌐 Environment
- **Node.js**: >= 14
- **npm**: >= 6