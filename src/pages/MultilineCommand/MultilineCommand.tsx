import React from "react";
import CodeBlock, { CodeText } from "../../components/CodeBlock";
import { Tab } from "../../components/CodeBlock/CodeBlock";
import useScrollToHash from "../../utils/scrollToHash";
import SidebarNav from "../../components/SidebarNav";

const MultilineCommand = () => {
    useScrollToHash();
    return (
        <section className="min-h-screen bg-primary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
            <div className="text-primary text-3xl md:text-6xl mx-auto">
                Multiline-command
            </div>
            <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                <p>
                    <Tab />
                    Unlike mcfunction, whitespaces in JMC doesn't effect the
                    code. You can have as many whitespaces within a command as
                    you want.
                </p>
                <p>
                    <Tab />
                    Whitespaces include spaces, tabs, newline(line feed), etc.
                    This means you can write a command as follow.
                </p>
                <CodeBlock>
                    execute
                    <br />
                    <Tab />
                    as <CodeText type="param">@a</CodeText>
                    <br />
                    <Tab />
                    at <CodeText type="param">@a</CodeText>
                    <br />
                    <Tab />
                    run <CodeText type="function">hello_world</CodeText>
                    ();
                    <br />
                    <br />
                    <CodeText type="keyword">function</CodeText>{" "}
                    <CodeText type="function">hello_world</CodeText>() {"{"}
                    <br />
                    <Tab />
                    <CodeText type="function">hi</CodeText>();
                    <br />
                    {"}"}
                    <br />
                    <br />
                    <CodeText type="keyword">function</CodeText>{" "}
                    <CodeText type="function">hi</CodeText>()
                    <br />
                    {"{"}
                    <br />
                    <Tab />
                    say <CodeText type="string">"Hello World"</CodeText>;
                    <br />
                    {"}"}
                </CodeBlock>
            </div>
        </section>
    );
};

export default MultilineCommand;
