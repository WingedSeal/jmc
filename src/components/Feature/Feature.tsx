import React from 'react'
import "./Feature.css";

interface FeatureInterface {
    id: string
    summary: string
    wip: boolean
    keywords: string
    children: React.ReactNode
}

const Feature: React.FC<FeatureInterface> = (props) => {
    return <div>
        <section id={props.id} />
        <details
            className={"border-4 border-solid border-[#ffedfa] rounded-2xl mb-4 p-3 transition-all ease-in-out duration-500 feature text-slate-200"
                + (props.wip ? ' not-done' : '')}
            id={props.id}
        >
            <summary className='transition-all ease-in-out duration-500 overflow-y-scroll scrollbar-none text-xl md:text-5xl cursor-pointer text-slate-100'>{props.summary}</summary>
            {props.children}
        </details>
    </div>
}

Feature.defaultProps = {
    keywords: "",
    wip: false
}

export default Feature
