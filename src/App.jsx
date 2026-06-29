import React, { useState, useMemo, useEffect } from 'react';
import { Search, MapPin, X, ChevronLeft, ChevronRight, Coins, Coffee, Users, Map, Compass, Grid, Map as MapIcon, ChevronRight as ArrowIcon } from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import shopsData from './data/shops.json';

// Leaflet default marker fix
const customIcon = new L.Icon({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});


// Helper component to change map viewport dynamically
function ChangeMapView({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
}

const AUTOSHOP_LOGO = "https://static.ladipage.net/5c45de506b9cc95d393350e9/autoshop-setup-copy-24x-20250409100752-rrewi.png";
const HERO_BG = "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?q=80&w=1600";

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('Tất cả');
  const [selectedProvince, setSelectedProvince] = useState('Tất cả');
  const [selectedShop, setSelectedShop] = useState(null);
  const [activeImageIdx, setActiveImageIdx] = useState(0);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'map'

  // Map viewport states
  const [mapCenter, setMapCenter] = useState([16.0, 106.5]);
  const [mapZoom, setMapZoom] = useState(6);

  // Reset province filter when region changes
  useEffect(() => {
    setSelectedProvince('Tất cả');
  }, [selectedRegion]);

  // Extract all unique provinces based on region selection
  const provinces = useMemo(() => {
    const list = new Set();
    shopsData.forEach(shop => {
      if (selectedRegion === 'Tất cả' || shop.region === selectedRegion) {
        if (shop.province) {
          list.add(shop.province);
        }
      }
    });
    return ['Tất cả', ...Array.from(list).sort()];
  }, [selectedRegion]);

  // Filter shops based on search query, region, and province
  const filteredShops = useMemo(() => {
    return shopsData.filter(shop => {
      const matchRegion = selectedRegion === 'Tất cả' || shop.region === selectedRegion;
      const matchProvince = selectedProvince === 'Tất cả' || shop.province === selectedProvince;
      
      const query = searchQuery.toLowerCase().trim();
      const matchSearch = !query || 
        (shop.name && shop.name.toLowerCase().includes(query)) ||
        (shop.address && shop.address.toLowerCase().includes(query)) ||
        (shop.province && shop.province.toLowerCase().includes(query)) ||
        (shop.model && shop.model.toLowerCase().includes(query));

      return matchRegion && matchProvince && matchSearch;
    });
  }, [searchQuery, selectedRegion, selectedProvince]);

  // Sync map center when filters change
  useEffect(() => {
    if (selectedProvince !== 'Tất cả') {
      const shopInProvince = filteredShops.find(s => s.province === selectedProvince);
      if (shopInProvince && shopInProvince.lat && shopInProvince.lng) {
        setMapCenter([shopInProvince.lat, shopInProvince.lng]);
        setMapZoom(12);
        return;
      }
    }
    if (selectedRegion !== 'Tất cả') {
      if (selectedRegion === 'Miền Bắc') {
        setMapCenter([21.0285, 105.8542]);
        setMapZoom(8);
      } else if (selectedRegion === 'Miền Trung') {
        setMapCenter([16.0544, 108.2022]);
        setMapZoom(8);
      } else if (selectedRegion === 'Miền Nam') {
        setMapCenter([10.8231, 106.6297]);
        setMapZoom(8);
      }
      return;
    }
    // Default center of Vietnam
    setMapCenter([16.0, 106.5]);
    setMapZoom(6);
  }, [selectedRegion, selectedProvince]);

  const openShopDetails = (shop) => {
    setSelectedShop(shop);
    setActiveImageIdx(0);
  };

  const closeShopDetails = () => {
    setSelectedShop(null);
  };

  const nextImage = (e) => {
    e.stopPropagation();
    if (!selectedShop || !selectedShop.images.length) return;
    setActiveImageIdx((prev) => (prev + 1) % selectedShop.images.length);
  };

  const prevImage = (e) => {
    e.stopPropagation();
    if (!selectedShop || !selectedShop.images.length) return;
    setActiveImageIdx((prev) => (prev - 1 + selectedShop.images.length) % selectedShop.images.length);
  };

  const handleSidebarItemClick = (shop) => {
    if (shop.lat && shop.lng) {
      setMapCenter([shop.lat, shop.lng]);
      setMapZoom(14); // Zoom closer
    }
  };

  return (
    <div className="app-wrapper">
      {/* Header navbar */}
      <header className="app-header">
        <div className="header-container">
          <div className="logo-section">
            <img src={AUTOSHOP_LOGO} alt="Autoshop Logo" className="logo-img" />
          </div>
        </div>
      </header>

      {/* Hero Banner with background image & Integrated Filters */}
      <section className="hero-banner" style={{ backgroundImage: `url(${HERO_BG})` }}>
        <div className="hero-overlay"></div>
        <div className="hero-container">
          <div className="hero-badge">
            <Compass size={14} />
            <span>Autoshop Setup Có Mặt Trên Toàn Quốc</span>
          </div>
          <h2 className="hero-title">Đồng Hành Kiến Tạo Khởi Nghiệp</h2>
          <p className="hero-subtitle">
            Hệ thống quản lý hàng trăm đối tác đã setup thành công khắp 3 miền Bắc - Trung - Nam với trang thiết bị hiện đại & quy chuẩn vận hành tối ưu.
          </p>
          
          {/* Integrated Search & Filter Control Panel */}
          <div className="hero-control-panel">
            {/* Row 1: Search Input */}
            <div className="hero-search-wrapper">
              <Search className="hero-search-icon" />
              <input
                type="text"
                placeholder="Nhập tên tỉnh thành, mô hình hoặc tên quán..."
                className="hero-search-input"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {searchQuery && (
                <button 
                  className="hero-search-clear"
                  onClick={() => setSearchQuery('')}
                  aria-label="Clear search"
                >
                  <X size={18} />
                </button>
              )}
            </div>

            {/* Row 2: Region Tabs & Province Select */}
            <div className="hero-filters-row">
              <div className="hero-region-tabs">
                {['Tất cả', 'Miền Bắc', 'Miền Trung', 'Miền Nam'].map((region) => (
                  <button
                    key={region}
                    className={`hero-region-tab ${selectedRegion === region ? 'active' : ''}`}
                    onClick={() => setSelectedRegion(region)}
                  >
                    {region}
                  </button>
                ))}
              </div>

              <div className="hero-select-wrapper">
                <select
                  className="hero-select-control"
                  value={selectedProvince}
                  onChange={(e) => setSelectedProvince(e.target.value)}
                >
                  {provinces.map((prov) => (
                    <option key={prov} value={prov}>
                      {prov === 'Tất cả' ? 'Tất cả Tỉnh / Thành' : prov}
                    </option>
                  ))}
                </select>
                <ChevronRight className="hero-select-arrow" style={{ transform: 'rotate(90deg)' }} />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Toggle view mode and results counter */}
        <div className="view-toggle-row">
          <div className="results-counter">
            Tìm thấy <strong>{filteredShops.length}</strong> kết quả phù hợp
          </div>
          <div className="toggle-buttons">
            <button 
              className={`toggle-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => setViewMode('grid')}
            >
              <Grid size={16} />
              <span>Xem dạng lưới</span>
            </button>
            <button 
              className={`toggle-btn ${viewMode === 'map' ? 'active' : ''}`}
              onClick={() => setViewMode('map')}
            >
              <MapIcon size={16} />
              <span>Xem bản đồ</span>
            </button>
          </div>
        </div>

        {/* Shop Display Area */}
        {viewMode === 'grid' ? (
          /* Grid View */
          <div className="shop-grid">
            {filteredShops.length > 0 ? (
              filteredShops.map((shop) => (
                <div 
                  key={shop.id} 
                  className="shop-card"
                  onClick={() => openShopDetails(shop)}
                >
                  <div className="card-img-wrapper">
                    <span className="region-badge">{shop.region}</span>
                    <span className="province-badge">{shop.province}</span>
                    <img 
                      src={shop.images[0] || "https://w.ladicdn.com/s800x800/5c45de506b9cc95d393350e9/autoshop-setup-copy-24x-20250409100752-rrewi.png"} 
                      alt={shop.name} 
                      className="card-img" 
                      loading="lazy"
                    />
                  </div>
                  <div className="card-info">
                    <h3 className="card-name">{shop.name || `Dự án tại ${shop.province}`}</h3>
                    <div className="card-address">
                      <MapPin className="icon" />
                      <span>{shop.address || shop.province}</span>
                    </div>
                    
                    {/* Badges metadata */}
                    {(shop.investment || shop.model) && (
                      <div className="card-metadata">
                        {shop.model && (
                          <span className="meta-badge model">
                            {shop.model.length > 20 ? `${shop.model.substring(0, 20)}...` : shop.model}
                          </span>
                        )}
                        {shop.investment && (
                          <span className="meta-badge investment">
                            {shop.investment}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="no-results">
                <h3>Không tìm thấy quán nào phù hợp</h3>
                <p>Thử nhập từ khóa khác hoặc điều chỉnh bộ lọc.</p>
              </div>
            )}
          </div>
        ) : (
          /* Interactive Map View with Sidebar List (Google My Maps style) */
          <div className="map-view-container">
            {/* Left Sidebar List */}
            <div className="map-sidebar">
              <div className="map-sidebar-title">Danh sách quán ({filteredShops.length})</div>
              <div className="map-sidebar-scroll">
                {filteredShops.length > 0 ? (
                  <ul className="map-sidebar-list">
                    {filteredShops.map((shop) => (
                      <li 
                        key={shop.id}
                        className="map-sidebar-item"
                        onClick={() => handleSidebarItemClick(shop)}
                      >
                        <div className="map-sidebar-item-header">
                          <span className="map-sidebar-item-name">{shop.name || `Dự án tại ${shop.province}`}</span>
                          <ArrowIcon size={14} className="map-sidebar-arrow" />
                        </div>
                        <p className="map-sidebar-item-address">{shop.address || shop.province}</p>
                        {shop.model && <span className="map-sidebar-item-badge">{shop.model}</span>}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="map-sidebar-empty">Không có dữ liệu</div>
                )}
              </div>
            </div>

            {/* Right Map Canvas */}
            <div className="map-canvas-area">
              <MapContainer 
                center={mapCenter} 
                zoom={mapZoom} 
                className="interactive-map"
                scrollWheelZoom={true}
              >
                <ChangeMapView center={mapCenter} zoom={mapZoom} />
                
                {/* Google Maps Tile Server in Vietnamese (hl=vi) */}
                <TileLayer
                  url="https://mt1.google.com/vt/lyrs=m&hl=vi&x={x}&y={y}&z={z}"
                  attribution='&copy; <a href="https://www.google.com/maps">Google Maps</a>'
                />
                

                {/* Shop Markers */}
                {filteredShops.map((shop) => (
                  shop.lat && shop.lng && (
                    <Marker 
                      key={shop.id} 
                      position={[shop.lat, shop.lng]} 
                      icon={customIcon}
                    >
                      <Popup className="shop-map-popup">
                        <div className="popup-card">
                          <img 
                            src={shop.images[0] || "https://w.ladicdn.com/s800x800/5c45de506b9cc95d393350e9/autoshop-setup-copy-24x-20250409100752-rrewi.png"} 
                            alt={shop.name} 
                            className="popup-img"
                          />
                          <div className="popup-info">
                            <h4 className="popup-name">{shop.name || `Dự án tại ${shop.province}`}</h4>
                            <p className="popup-address">{shop.address || shop.province}</p>
                            {shop.model && <span className="popup-badge">{shop.model}</span>}
                            <button 
                              className="popup-view-btn"
                              onClick={() => openShopDetails(shop)}
                            >
                              Xem chi tiết
                            </button>
                          </div>
                        </div>
                      </Popup>
                    </Marker>
                  )
                ))}
              </MapContainer>
            </div>
          </div>
        )}
      </main>

      {/* Modal Details Popup */}
      {selectedShop && (
        <div className="modal-overlay" onClick={closeShopDetails}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={closeShopDetails} aria-label="Close modal">
              <X />
            </button>
            
            <div className="modal-scrollable">
              <div className="modal-grid">
                {/* Left Column: Image Slider */}
                <div className="carousel-container">
                  <div className="main-image-wrapper">
                    {selectedShop.images.length > 1 && (
                      <>
                        <button className="nav-arrow prev" onClick={prevImage} aria-label="Previous image">
                          <ChevronLeft />
                        </button>
                        <button className="nav-arrow next" onClick={nextImage} aria-label="Next image">
                          <ChevronRight />
                        </button>
                      </>
                    )}
                    <img 
                      src={selectedShop.images[activeImageIdx] || "https://w.ladicdn.com/s800x800/5c45de506b9cc95d393350e9/autoshop-setup-copy-24x-20250409100752-rrewi.png"} 
                      alt={selectedShop.name} 
                      className="main-image"
                    />
                  </div>
                  
                  {/* Thumbnails strip */}
                  {selectedShop.images.length > 1 && (
                    <div className="thumbnail-strip">
                      {selectedShop.images.map((imgUrl, idx) => (
                        <div 
                          key={idx} 
                          className={`thumbnail-wrapper ${activeImageIdx === idx ? 'active' : ''}`}
                          onClick={() => setActiveImageIdx(idx)}
                        >
                          <img src={imgUrl} alt={`Thumbnail ${idx}`} className="thumbnail-img" />
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Right Column: Spec Table */}
                <div className="spec-container">
                  <div className="spec-title-section">
                    <div className="spec-province">{selectedShop.province} - {selectedShop.region}</div>
                    <h2 className="spec-name">{selectedShop.name || `Dự án tại ${selectedShop.province}`}</h2>
                  </div>
                  
                  <table className="spec-table">
                    <tbody>
                      <tr className="spec-row">
                        <td className="spec-label">Tỉnh / Thành:</td>
                        <td className="spec-val">{selectedShop.province}</td>
                      </tr>
                      <tr className="spec-row">
                        <td className="spec-label">Địa Chỉ:</td>
                        <td className="spec-val">{selectedShop.address || selectedShop.province}</td>
                      </tr>
                      <tr className="spec-row">
                        <td className="spec-label">Tổng Đầu Tư:</td>
                        <td className="spec-val">{selectedShop.investment || "Đang cập nhật"}</td>
                      </tr>
                      <tr className="spec-row">
                        <td className="spec-label">Mô Hình Quán:</td>
                        <td className="spec-val">{selectedShop.model || "Đang cập nhật"}</td>
                      </tr>
                      <tr className="spec-row">
                        <td className="spec-label">Tệp Khách Hàng:</td>
                        <td className="spec-val">{selectedShop.target_customers || "Đang cập nhật"}</td>
                      </tr>
                    </tbody>
                  </table>

                  {/* Google Maps Search Link */}
                  <a 
                    href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(selectedShop.name + ' ' + (selectedShop.address || selectedShop.province))}`}
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="google-maps-btn"
                  >
                    <Map size={18} />
                    <span>Xem vị trí trên Google Maps</span>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
