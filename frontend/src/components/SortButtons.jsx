import './SortButtons.css';

export default function SortButtons({ onSort }) {
    return (
        <div className="sorting-container">
            <button
                className="sort-btn"
                onClick={() => onSort('price_asc')}
            >
                Price: Low → High
            </button>
            <button
                className="sort-btn"
                onClick={() => onSort('price_desc')}
            >
                Price: High → Low
            </button>
            <button
                className="sort-btn"
                onClick={() => onSort('name')}
            >
                Name: A → Z
            </button>
        </div>
    );
}
