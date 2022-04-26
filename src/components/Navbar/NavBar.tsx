import React, { useRef } from "react";
import { Link, useLocation } from "react-router-dom";
import "./NavBar.css";

const NavBar = () => {
    const exampleBtn = useRef<HTMLUListElement>(null);
    const documentationBtn = useRef<HTMLUListElement>(null);
    const gettingStartedBtn = useRef<HTMLUListElement>(null);
    return (
        <nav className="sticky top-0 flex flex-row h-[11vh] w-screen items-center bg-black">
            <Link to="/" className="h-3/4 mx-10 aspect-square">
                <img
                    className="h-full"
                    src={require("../../assets/image/jmc_icon.png")}
                    alt="JMC-icon"
                />
            </Link>
            <div className="flex-initial w-1/2"></div>
            <ul className="flex flex-row flex-auto justify-around flex-nowrap mr-10 text-lg whitespace-nowrap text-white">
                <li className="mx-1">
                    <LinkItem to="/">Home</LinkItem>
                </li>
                <li className="mx-1">
                    <LinkItem to="/download">Download</LinkItem>
                </li>
                <li className="mx-1 relative">
                    <DropDownButton
                        to="/getting-started"
                        ulRef={gettingStartedBtn}
                    >
                        Getting-Started
                    </DropDownButton>

                    <ul
                        className="absolute p-2 border border-white bg-black/50 rounded-lg mt-2 transition-transform"
                        style={{ transform: "scaleY(0)" }}
                        ref={gettingStartedBtn}
                    >
                        <LinkItem to="/getting-started/introduction">
                            Introduction
                        </LinkItem>
                        <LinkItem to="/getting-started/how-it-works">
                            How it works
                        </LinkItem>
                        <LinkItem to="/getting-started/installation">
                            Installation
                        </LinkItem>
                        <LinkItem to="/getting-started/code">Code</LinkItem>
                    </ul>
                </li>
                <li className="mx-1 relative">
                    <DropDownButton
                        to="/documentation"
                        ulRef={documentationBtn}
                    >
                        Documentation
                    </DropDownButton>

                    <ul
                        className="absolute p-2 border border-white bg-black/50 rounded-lg mt-2 transition-transform"
                        style={{ transform: "scaleY(0)" }}
                        ref={documentationBtn}
                    >
                        <LinkItem to="/documentation/multiline-command">
                            Multiline-Command
                        </LinkItem>
                        <LinkItem to="/documentation/import">Import</LinkItem>
                        <LinkItem to="/documentation/comment">Comment</LinkItem>
                        <LinkItem to="/documentation/load-tick">
                            Load/Tick
                        </LinkItem>
                        <LinkItem to="/documentation/variable">
                            Variable
                        </LinkItem>
                        <LinkItem to="/documentation/flow-controls">
                            Flow Controls
                        </LinkItem>
                        <LinkItem to="/documentation/json-files">
                            JSON Files
                        </LinkItem>
                        <LinkItem to="/documentation/built-in-function">
                            Built-in Function
                        </LinkItem>
                    </ul>
                </li>
                <li className="mx-1 relative">
                    <DropDownButton to="/examples" ulRef={exampleBtn}>
                        Examples
                    </DropDownButton>
                    <ul
                        className="absolute p-2 border border-white bg-black/50 rounded-lg mt-2 transition-transform"
                        style={{ transform: "scaleY(0)" }}
                        ref={exampleBtn}
                    >
                        <LinkItem to="/examples/basics">Basics</LinkItem>
                        <LinkItem to="/examples/advanced">Advanced</LinkItem>
                        <LinkItem to="/examples/submitted">Submitted</LinkItem>
                    </ul>
                </li>
            </ul>
        </nav>
    );
};

export default NavBar;

interface LinkItemProps {
    to: string;
    children?: React.ReactChild;
}

const LinkItem: React.FC<LinkItemProps> = ({ to, children }) => {
    const path = useLocation().pathname;
    const active = path === to;
    return (
        <div className="hover:scale-105 transition-transform duration-100 active:scale-95 select-none">
            <Link to={to}>
                <div className={active ? "glow " : ""}>{children}</div>
            </Link>
        </div>
    );
};

interface DropDownLabelProp {
    to: string;
    htmlFor: string;
    children?: React.ReactChild;
}

const DropDownLabel: React.FC<DropDownLabelProp> = ({
    htmlFor,
    to,
    children,
}) => {
    const path = useLocation().pathname;
    const active = path.startsWith(to);
    return (
        <div className="hover:scale-105 transition-transform duration-100 active:scale-100">
            <div className={active ? "glow" : ""}>
                <label className="cursor-pointer select-none" htmlFor={htmlFor}>
                    {children}
                </label>
            </div>
        </div>
    );
};

interface DropDownButtonProp {
    to: string;
    ulRef: React.RefObject<HTMLUListElement>;
    children?: React.ReactChild;
}

const DropDownButton: React.FC<DropDownButtonProp> = ({
    ulRef,
    to,
    children,
}) => {
    const path = useLocation().pathname;
    const active = path.startsWith(to);
    return (
        <div className="hover:scale-105 transition-transform duration-100 active:scale-100">
            <div className={active ? "glow" : ""}>
                <button
                    className="cursor-pointer select-none"
                    onClick={() => {
                        const ulElement = ulRef.current!;
                        if (ulElement.classList.contains("open")) {
                            ulElement.classList.remove("open");
                            ulElement.style.transform = "scaleY(0%)";
                        } else {
                            ulElement.classList.add("open");
                            ulElement.style.transform = "scaleY(100%)";
                        }
                    }}
                >
                    {children}
                </button>
            </div>
        </div>
    );
};
