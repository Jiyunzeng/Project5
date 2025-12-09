import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import './MainPage.css';

function MainPage() {
    const [activeTab, setActiveTab] = useState('stock');
    const [searchTerm, setSearchTerm] = useState('');
    const [results, setResults] = useState([]);
    const [searched, setSearched] = useState(false); // 검색 버튼 눌렀는지 여부
    const [loading, setLoading] = useState(false);   // ✅ 검색중 상태
    const navigate = useNavigate();

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!searchTerm.trim()) return;

        setSearched(true);
        setLoading(true);   // ✅ 검색 시작

        if (activeTab === 'news') {
            navigate(`/news?keyword=${encodeURIComponent(searchTerm)}`);
        } else {
            try {
                const kospiRes = await fetch("/api/krx/kospi/list");
                const kosdaqRes = await fetch("/api/krx/kosdaq/list");
                const kospi = await kospiRes.json();
                const kosdaq = await kosdaqRes.json();

                const allStocks = [...kospi, ...kosdaq];
                const filtered = allStocks.filter((s) =>
                    s.name.includes(searchTerm)
                );
                setResults(filtered);
            } catch (err) {
                console.error("주식 검색 실패:", err);
            } finally {
                setLoading(false);   // ✅ 검색 완료
            }
        }
    };

    return (
        <div className="main-container">
            <h1 className="main-title">Stock & News Search</h1>

            <div className="glass-card">
                <div className="tabs">
                    <button
                        onClick={() => setActiveTab('stock')}
                        className={`tab ${activeTab === 'stock' ? 'tab-active' : ''}`}
                    >
                        주식 검색
                    </button>
                    <button
                        onClick={() => setActiveTab('news')}
                        className={`tab ${activeTab === 'news' ? 'tab-active' : ''}`}
                    >
                        뉴스 검색
                    </button>
                </div>

                <form onSubmit={handleSearch} className="search-form">
                    <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder={
                            activeTab === 'stock'
                                ? '삼성전자, 애플, 테슬라, 엔비디아...'
                                : '경제 뉴스, 기업명, 키워드...'
                        }
                        className="search-input"
                        autoFocus
                    />
                    <button type="submit" className="search-btn">검색</button>

                    {/* 🔑 초기화 버튼 */}
                    <button
                        type="button"
                        className="reset-btn"
                        onClick={() => {
                            setSearchTerm("");
                            setResults([]);
                            setSearched(false);
                        }}
                    >
                        초기화
                    </button>
                </form>

                {/* 🔑 검색 결과 표시 */}
                {activeTab === 'stock' && (
                    <>
                        {loading ? (
                            <p className="loading-text">검색중...</p>
                        ) : results.length > 0 ? (
                            <ul className="search-results">
                                {results.map((s) => (
                                    <li key={s.code}>
                                        <button
                                            className="result-item"
                                            onClick={() => navigate(`/krx/${s.code}`)}
                                        >
                                            {s.name} ({s.code})
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            searched && <p className="no-results">검색 결과가 없습니다</p>
                        )}
                    </>
                )
                }
            </div>
        </div>
    )
        ;
}

export default MainPage;
