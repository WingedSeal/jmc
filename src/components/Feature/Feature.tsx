import React from "react";
import "./Feature.css";

interface FeatureInterface {
    id: string;
    summary: string;
    keywords: string;
    children: React.ReactNode;
    className?: string;
    wip?: boolean;
}

const Feature: React.FC<FeatureInterface> = (props) => {
    return (
        <div>
            <section id={props.id} />
            <details
                className={
                    "border-4 border-solid border-[#ffedfa] rounded-2xl mb-4 p-3 md:p-5 transition-all ease-in-out duration-500 feature text-slate-200" +
                    (props.wip ? " not-done" : "")
                }
                id={props.id}
            >
                <summary
                    className={
                        "transition-all ease-in-out duration-500 overflow-y-scroll scrollbar-none text-xl md:text-5xl cursor-pointer text-slate-100 " +
                        props.className
                    }
                >
                    {props.summary}
                </summary>
                {props.children}
                <div className="mb-2" />
            </details>
        </div>
    );
};

Feature.defaultProps = {
    keywords: "",
    className: "",
    wip: false,
};

export default Feature;
