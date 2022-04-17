import React from "react";
import "./Feature.css";

interface Props {
    children?: React.ReactNode;
    summary: string;
}

const Feature: React.FC<Props> = ({ children, summary }) => {
    return (
        <details className="feature">
            <summary>
                <div className="icon" />
                <span className="text">{summary}</span>
            </summary>

            <div className="child">{children}</div>
        </details>
    );
};

export default Feature;
