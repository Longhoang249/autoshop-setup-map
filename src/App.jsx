import React, { useState, useMemo, useEffect } from 'react';
import { Search, MapPin, X, ChevronLeft, ChevronRight, Coins, Coffee, Users, Map } from 'lucide-react';
import shopsData from './data/shops.json';

const AUTOSHOP_LOGO = "https://static.ladipage.net/5c45de506b9cc95d393350e9/autoshop-setup-copy-24x-20250409100752-rrewi.png";

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('Tất cả');
  const [selectedProvince, setSelectedProvince] = useState('Tất cả');
  const [selectedShop, setSelectedShop] = useState(null);
  const [activeImageIdx, setActiveImageIdx] = useState(0);

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

  // Statistics counters
  const stats = useMemo(() => {
    const total = shopsData.length;
    const mienBac = shopsData.filter(s => s.region === 'Miền Bắc').length;
    const mienTrung = shopsData.filter(s => s.region === 'Miền Trung').length;
    const mienNam = shopsData.filter(s => s.region === 'Miền Nam').length;
    return { total, mienBac, mienTrung, mienNam };
  }, []);

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

  return (
    <div className="app-wrapper">
      {/* Header navbar */}
      <header className="app-header">
        <div className="header-container">
          <div className="logo-section">
            <img src={AUTOSHOP_LOGO} alt="Autoshop Logo" className="logo-img" />
            <h1 className="logo-text">Autoshop Setup</h1>
          </div>
        </div>
      </header>

      {/* Hero Banner */}
      <section className="hero-banner">
        <div className="hero-container">
          <h2 className="hero-title">Bản Đồ Setup Quán Việt Nam</h2>
          <p className="hero-subtitle">
            Hành trình đồng hành cùng hơn {stats.total} chủ quán khởi nghiệp thành công trên khắp cả nước. Thiết bị hiện đại, quy trình bar chuẩn mực.
          </p>
          
          <div className="stats-container">
            <div className="stat-item">
              <span className="stat-val">{stats.total}</span>
              <span className="stat-lbl">Tổng quán</span>
            </div>
            <div className="stat-item">
              <span className="stat-val">{stats.mienBac}</span>
              <span className="stat-lbl">Miền Bắc</span>
            </div>
            <div className="stat-item">
              <span className="stat-val">{stats.mienTrung}</span>
              <span className="stat-lbl">Miền Trung</span>
            </div>
            <div className="stat-item">
              <span className="stat-val">{stats.mienNam}</span>
              <span className="stat-lbl">Miền Nam</span>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Filters Card */}
        <div className="filter-card">
          <div className="filter-grid">
            {/* Search Input */}
            <div className="search-input-wrapper">
              <Search className="search-icon" />
              <input
                type="text"
                placeholder="Tìm tên quán, địa chỉ, mô hình..."
                className="search-input"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {/* Region Tabs */}
            <div className="region-tabs">
              {['Tất cả', 'Miền Bắc', 'Miền Trung', 'Miền Nam'].map((region) => (
                <button
                  key={region}
                  className={`region-tab ${selectedRegion === region ? 'active' : ''}`}
                  onClick={() => setSelectedRegion(region)}
                >
                  {region}
                </button>
              ))}
            </div>

            {/* Province Selection */}
            <div className="select-wrapper">
              <select
                className="select-control"
                value={selectedProvince}
                onChange={(e) => setSelectedProvince(e.target.value)}
              >
                {provinces.map((prov) => (
                  <option key={prov} value={prov}>
                    {prov === 'Tất cả' ? 'Chọn Tỉnh / Thành phố' : prov}
                  </option>
                ))}
              </select>
              <ChevronRight className="select-arrow" style={{ transform: 'rotate(90deg)' }} />
            </div>
          </div>
        </div>

        {/* Shop List Grid */}
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

                  {/* Standard Map Button (Placeholder or Maps search link) */}
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
