import { useMemo } from 'react';
import './CategoryDropdown.css';

export default function CategoryDropdown({ categories, selectedCategory, onCategoryChange, isOpen, onToggle }) {
    const selectedLabel = useMemo(() => {
        return categories.find((cat) => cat.value === selectedCategory)?.label ?? 'All';
    }, [categories, selectedCategory]);

    const handleCategorySelect = (category) => {
        onCategoryChange(category.value);
        if (onToggle) {
            onToggle(false);
        }
    };

    return (
        <div className="dropdown">
            <button
                className="dropbtn"
                onClick={() => onToggle && onToggle(!isOpen)}
            >
                {selectedLabel} ▼
            </button>
            <div
                className={`dropdown-content ${isOpen ? 'show' : ''}`}
            >
                {categories.map((cat) => (
                    <button
                        key={cat.value}
                        type="button"
                        className="dropdown-item"
                        onClick={() => handleCategorySelect(cat)}
                    >
                        {cat.label}
                    </button>
                ))}
            </div>
        </div>
    );
}
