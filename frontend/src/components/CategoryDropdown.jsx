import { useMemo, useState } from 'react';
import './CategoryDropdown.css';

export default function CategoryDropdown({ categories, selectedCategory, onCategoryChange }) {
    const [isOpen, setIsOpen] = useState(false);

    const selectedLabel = useMemo(() => {
        return categories.find((cat) => cat.value === selectedCategory)?.label ?? 'All';
    }, [categories, selectedCategory]);

    const handleCategorySelect = (category) => {
        onCategoryChange(category.value);
        setIsOpen(false);
    };

    return (
        <div className="dropdown">
            <button
                className="dropbtn"
                onClick={() => setIsOpen(!isOpen)}
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
