import React, { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { ReactComponent as MenuSvg } from "../../assets/image/menu.svg";
import "./NavBar.css";

const NavBar = () => {
    const exampleBtn = useRef<HTMLUListElement>(null);
    const documentationBtn = useRef<HTMLUListElement>(null);
    const gettingStartedBtn = useRef<HTMLUListElement>(null);
    const exampleBtnMobile = useRef<HTMLUListElement>(null);
    const documentationBtnMobile = useRef<HTMLUListElement>(null);
    const gettingStartedBtnMobile = useRef<HTMLUListElement>(null);
    const mobileMenu = useRef<HTMLUListElement>(null);
    const mobileLeftMenu = useRef<HTMLDivElement>(null);
    const mobileMenuButton = useRef<HTMLButtonElement>(null);
    const ulRefs = [exampleBtn, documentationBtn, gettingStartedBtn];
    const ulRefsMobile = [
        exampleBtnMobile,
        documentationBtnMobile,
        gettingStartedBtnMobile,
    ];

    const oldScrollY = useRef(window.scrollY);
    const [scrollY, setScrollY] = useState(window.scrollY);
    const [isScrollUp, setIsScrollUp] = useState(false);
    const handleScroll = () => {
        setIsScrollUp(window.scrollY < oldScrollY.current);
        setScrollY(window.scrollY);
        oldScrollY.current = window.scrollY;
    };

    useEffect(() => {
        window.addEventListener("scroll", handleScroll, { passive: true });
        // window.addEventListener("resize", handleWindowResize, {
        //     passive: true,
        // });
        return () => {
            window.removeEventListener("scroll", handleScroll);
            // window.removeEventListener("resize", handleWindowResize);
        };
    }, []);

    useEffect(() => {
        if (!isScrollUp) {
            for (const ulRef of ulRefs) {
                closeUlRef(ulRef);
            }
        }
        // eslint-disable-next-line
    }, [isScrollUp]);

    const path = useLocation().pathname;
    return (
        <nav
            className={
                "fixed top-0 flex flex-row h-[11vh] w-screen items-center transition-[transform,background-color] duration-500 z-10 " +
                (scrollY < 1 && path === "/" ? "bg-transparent" : "bg-black") +
                " " +
                (!isScrollUp && scrollY !== 0 ? "-translate-y-full" : "")
            }
        >
            <Link to="/" className="h-3/4 mx-10 aspect-square">
                <img
                    className="h-full"
                    src={require("../../assets/image/jmc_icon.png")}
                    alt="JMC-icon"
                />
            </Link>
            <div className="flex-initial w-1/2"></div>
            {/* Mobile */}
            <button
                className="block mr-5 ml-auto md:hidden z-20"
                ref={mobileMenuButton}
                onClick={() => {
                    const menu = mobileMenu.current!;
                    const leftMenu = mobileLeftMenu.current!;
                    if (menu.classList.contains("open")) {
                        // CLOSE
                        menu.classList.remove("open");
                        menu.style.transform = "translateX(100%)";
                        leftMenu.style.display = "none";
                        document.body.style.overflowY = "unset";
                    } else {
                        // OPEN
                        menu.classList.add("open");
                        menu.style.transform = "translateX(0%)";
                        leftMenu.style.display = "block";
                        document.body.style.overflowY = "hidden";
                    }
                }}
            >
                <MenuSvg />
            </button>
            <div
                className="left-0 top-0 h-screen w-[15vw] absolute z-10 md:!hidden cursor-pointer"
                ref={mobileLeftMenu}
                style={{ display: "none" }}
                onClick={() => {
                    const menu = mobileMenu.current!;
                    const leftMenu = mobileLeftMenu.current!;
                    menu.classList.remove("open");
                    menu.style.transform = "translateX(100%)";
                    leftMenu.style.display = "none";
                    document.body.style.overflow = "unset";
                }}
            />
            <ul
                ref={mobileMenu}
                className="transition-transform right-0 top-0 h-screen w-[85vw] bg-black/90 absolute z-10 overflow-y-scroll flex flex-col justify-start align-bottom text-3xl text-white md:hidden"
                style={{ transform: "translateX(100%)" }}
            >
                <li className="mr-5 ml-auto mt-20">
                    <LinkItem to="/" ulRefs={ulRefsMobile}>
                        Home
                    </LinkItem>
                </li>
                <li className="mr-5 ml-auto mt-3">
                    <LinkItem to="/download" ulRefs={ulRefsMobile}>
                        Download
                    </LinkItem>
                </li>
                <li className="mr-5 ml-auto relative mt-3 flex justify-end">
                    <DropDownButton
                        to="/getting-started"
                        ulRef={gettingStartedBtnMobile}
                        others={[documentationBtnMobile, exampleBtnMobile]}
                    >
                        Getting-Started
                    </DropDownButton>

                    <ul
                        className="absolute p-2 border border-white bg-black/80 rounded-lg mt-2 transition-transform z-20 top-[100%] text-2xl"
                        style={{ transform: "scaleY(0)" }}
                        ref={gettingStartedBtnMobile}
                    >
                        <LinkItem
                            to="/getting-started/introduction"
                            ulRefs={ulRefsMobile}
                        >
                            Introduction
                        </LinkItem>
                        <LinkItem
                            to="/getting-started/how-it-works"
                            ulRefs={ulRefsMobile}
                        >
                            How it works
                        </LinkItem>
                        <LinkItem
                            to="/getting-started/installation"
                            ulRefs={ulRefsMobile}
                        >
                            Installation
                        </LinkItem>
                        <LinkItem
                            to="/getting-started/code"
                            ulRefs={ulRefsMobile}
                        >
                            Code
                        </LinkItem>
                    </ul>
                </li>
                <li className="mr-5 ml-auto relative mt-3 flex justify-end">
                    <DropDownButton
                        to="/documentation"
                        ulRef={documentationBtnMobile}
                        others={[gettingStartedBtnMobile, exampleBtnMobile]}
                    >
                        Documentation
                    </DropDownButton>

                    <ul
                        className="absolute p-2 border border-white bg-black/80 rounded-lg mt-2 transition-transform z-20 top-[100%] text-2xl leading-6 space-y-2"
                        style={{ transform: "scaleY(0)" }}
                        ref={documentationBtnMobile}
                    >
                        <LinkItem
                            to="/documentation/multiline-command"
                            ulRefs={ulRefsMobile}
                        >
                            Multiline-Command
                        </LinkItem>
                        <LinkItem
                            to="/documentation/import"
                            ulRefs={ulRefsMobile}
                        >
                            Import
                        </LinkItem>
                        <LinkItem
                            to="/documentation/comment"
                            ulRefs={ulRefsMobile}
                        >
                            Comment
                        </LinkItem>
                        <LinkItem
                            to="/documentation/function"
                            ulRefs={ulRefsMobile}
                        >
                            Function
                        </LinkItem>
                        <LinkItem
                            to="/documentation/load-tick"
                            ulRefs={ulRefsMobile}
                        >
                            Load/Tick
                        </LinkItem>
                        <LinkItem
                            to="/documentation/variable"
                            ulRefs={ulRefsMobile}
                        >
                            Variable
                        </LinkItem>
                        <LinkItem
                            to="/documentation/flow-controls"
                            ulRefs={ulRefsMobile}
                        >
                            Flow Controls
                        </LinkItem>
                        <LinkItem
                            to="/documentation/json-files"
                            ulRefs={ulRefsMobile}
                        >
                            JSON Files
                        </LinkItem>
                        <LinkItem
                            to="/documentation/built-in-function"
                            ulRefs={ulRefsMobile}
                        >
                            Built-in Function
                        </LinkItem>
                        <LinkItem
                            to="/documentation/header"
                            ulRefs={ulRefsMobile}
                        >
                            Header
                        </LinkItem>
                    </ul>
                </li>
                <li className="mr-5 ml-auto relative mt-3 flex justify-end">
                    <DropDownButton
                        to="/examples"
                        ulRef={exampleBtnMobile}
                        others={[
                            gettingStartedBtnMobile,
                            documentationBtnMobile,
                        ]}
                    >
                        Examples
                    </DropDownButton>
                    <ul
                        className="absolute p-2 border border-white bg-black/80 rounded-lg mt-2 transition-transform z-20 top-[100%] text-2xl"
                        style={{ transform: "scaleY(0)" }}
                        ref={exampleBtnMobile}
                    >
                        <LinkItem to="/examples/basics" ulRefs={ulRefsMobile}>
                            Basics
                        </LinkItem>
                        <LinkItem to="/examples/advanced" ulRefs={ulRefsMobile}>
                            Advanced
                        </LinkItem>
                        <LinkItem
                            to="/examples/submitted"
                            ulRefs={ulRefsMobile}
                        >
                            Submitted
                        </LinkItem>
                    </ul>
                </li>
            </ul>

            {/* Large Screen */}
            <ul className="flex-row flex-auto justify-around flex-nowrap mr-10 text-lg whitespace-nowrap text-white hidden md:flex">
                <li className="mx-1">
                    <LinkItem to="/" ulRefs={ulRefs}>
                        Home
                    </LinkItem>
                </li>
                <li className="mx-1">
                    <LinkItem to="/download" ulRefs={ulRefs}>
                        Download
                    </LinkItem>
                </li>
                <li className="mx-1 relative">
                    <DropDownButton
                        to="/getting-started"
                        ulRef={gettingStartedBtn}
                        others={[documentationBtn, exampleBtn]}
                    >
                        Getting-Started
                    </DropDownButton>

                    <ul
                        className="absolute p-2 border border-white bg-black/50 rounded-lg mt-2 transition-transform"
                        style={{ transform: "scaleY(0)" }}
                        ref={gettingStartedBtn}
                    >
                        <LinkItem
                            to="/getting-started/introduction"
                            ulRefs={ulRefs}
                        >
                            Introduction
                        </LinkItem>
                        <LinkItem
                            to="/getting-started/how-it-works"
                            ulRefs={ulRefs}
                        >
                            How it works
                        </LinkItem>
                        <LinkItem
                            to="/getting-started/installation"
                            ulRefs={ulRefs}
                        >
                            Installation
                        </LinkItem>
                        <LinkItem to="/getting-started/code" ulRefs={ulRefs}>
                            Code
                        </LinkItem>
                    </ul>
                </li>
                <li className="mx-1 relative">
                    <DropDownButton
                        to="/documentation"
                        ulRef={documentationBtn}
                        others={[gettingStartedBtn, exampleBtn]}
                    >
                        Documentation
                    </DropDownButton>

                    <ul
                        className="absolute p-2 border border-white bg-black/50 rounded-lg mt-2 transition-transform"
                        style={{ transform: "scaleY(0)" }}
                        ref={documentationBtn}
                    >
                        <LinkItem
                            to="/documentation/multiline-command"
                            ulRefs={ulRefs}
                        >
                            Multiline-Command
                        </LinkItem>
                        <LinkItem to="/documentation/import" ulRefs={ulRefs}>
                            Import
                        </LinkItem>
                        <LinkItem to="/documentation/comment" ulRefs={ulRefs}>
                            Comment
                        </LinkItem>
                        <LinkItem to="/documentation/function" ulRefs={ulRefs}>
                            Function
                        </LinkItem>
                        <LinkItem to="/documentation/load-tick" ulRefs={ulRefs}>
                            Load/Tick
                        </LinkItem>
                        <LinkItem to="/documentation/variable" ulRefs={ulRefs}>
                            Variable
                        </LinkItem>
                        <LinkItem
                            to="/documentation/flow-controls"
                            ulRefs={ulRefs}
                        >
                            Flow Controls
                        </LinkItem>
                        <LinkItem
                            to="/documentation/json-files"
                            ulRefs={ulRefs}
                        >
                            JSON Files
                        </LinkItem>
                        <LinkItem
                            to="/documentation/built-in-function"
                            ulRefs={ulRefs}
                        >
                            Built-in Function
                        </LinkItem>
                        <LinkItem to="/documentation/header" ulRefs={ulRefs}>
                            Header
                        </LinkItem>
                    </ul>
                </li>
                <li className="mx-1 relative">
                    <DropDownButton
                        to="/examples"
                        ulRef={exampleBtn}
                        others={[gettingStartedBtn, documentationBtn]}
                    >
                        Examples
                    </DropDownButton>
                    <ul
                        className="absolute p-2 border border-white bg-black/50 rounded-lg mt-2 transition-transform"
                        style={{ transform: "scaleY(0)" }}
                        ref={exampleBtn}
                    >
                        <LinkItem to="/examples/basics" ulRefs={ulRefs}>
                            Basics
                        </LinkItem>
                        <LinkItem to="/examples/advanced" ulRefs={ulRefs}>
                            Advanced
                        </LinkItem>
                        <LinkItem to="/examples/submitted" ulRefs={ulRefs}>
                            Submitted
                        </LinkItem>
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
    ulRefs: Array<React.RefObject<HTMLUListElement>>;
}

const LinkItem: React.FC<LinkItemProps> = ({ to, children, ulRefs }) => {
    const path = useLocation().pathname;
    const active = path === to;
    return (
        <div className="hover:scale-105 transition-transform duration-100 active:scale-95 select-none">
            <Link
                to={to}
                onClick={() => {
                    setTimeout(() => {
                        for (const ulRef of ulRefs) {
                            closeUlRef(ulRef);
                        }
                    }, 200);
                }}
            >
                <div className={active ? "glow " : ""}>{children}</div>
            </Link>
        </div>
    );
};

interface DropDownButtonProp {
    to: string;
    ulRef: React.RefObject<HTMLUListElement>;
    others: Array<React.RefObject<HTMLUListElement>>;
    children?: React.ReactChild;
}

const DropDownButton: React.FC<DropDownButtonProp> = ({
    ulRef,
    to,
    children,
    others,
}) => {
    const path = useLocation().pathname;
    const active = path.startsWith(to);
    return (
        <div className="hover:scale-105 transition-transform duration-100 active:scale-100 glow">
            <button
                className={
                    active
                        ? "glow cursor-pointer select-none"
                        : "cursor-pointer select-none"
                }
                onClick={() => {
                    toggleUlRef(ulRef);
                    for (const ulRef of others) {
                        closeUlRef(ulRef);
                    }
                }}
            >
                {children}
            </button>
        </div>
    );
};

function toggleUlRef(ulRef: React.RefObject<HTMLUListElement>) {
    const ulElement = ulRef.current!;
    if (ulElement.classList.contains("open")) {
        ulElement.classList.remove("open");
        ulElement.style.transform = "scaleY(0%)";
    } else {
        ulElement.classList.add("open");
        ulElement.style.transform = "scaleY(100%)";
    }
}

function closeUlRef(ulRef: React.RefObject<HTMLUListElement>) {
    const ulElement = ulRef.current!;
    if (ulElement.classList.contains("open")) {
        ulElement.classList.remove("open");
        ulElement.style.transform = "scaleY(0%)";
    }
}
