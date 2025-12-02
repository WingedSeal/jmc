import React from "react";
import CodeBlock, { CodeText } from "../../components/CodeBlock";
import { Tab } from "../../components/CodeBlock/CodeBlock";
import useScrollToHash from "../../utils/scrollToHash";
import SectionLinkCopy from "../../components/SectionLinkCopy";

const Decorator = () => {
    useScrollToHash();
    return (
        <>
            <section className="min-h-screen bg-secondary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
                <div className="text-secondary text-3xl md:text-6xl mx-auto">
                    Function Decorator
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />A feature to modify a function's behavior by
                        putting <code>@decoratorName</code> in front of a
                        function declaration.
                    </p>
                    <CodeBlock>
                        <CodeText type="param">@decoratorName</CodeText>
                        <br />
                        <CodeText type="keyword">function</CodeText>{" "}
                        <CodeText type="function">functionName</CodeText>
                        () {"{"} <br />
                        <Tab />
                        say{" "}
                        <CodeText type="string">"Function Content"</CodeText>;
                        <br />
                        {"}"}
                    </CodeBlock>
                </div>

                <section id="add" />
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Add
                    <SectionLinkCopy sectionId="add" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Call the current function from the function provided in
                        the decorator
                    </p>
                    <CodeBlock>
                        <CodeText type="param">@add(__tick__)</CodeText>
                        <br />
                        <CodeText type="keyword">function</CodeText>{" "}
                        <CodeText type="function">functionName</CodeText>
                        () {"{"} <br />
                        <Tab />
                        say{" "}
                        <CodeText type="string">"Function Content"</CodeText>;
                        <br />
                        {"}"}
                    </CodeBlock>
                </div>
                <section id="lazy" />
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Lazy
                    <SectionLinkCopy sectionId="lazy" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Compile time function similar to macro. This'll allow a
                        function to be evaluated when used and allow compile
                        time parameters. Instead of creating a new mcfunction
                        directly like regular function do, lazy function will
                        copy the content inside into where ever you call it.
                        Unlike mcfunction, lazy function has to be defined
                        BEFORE using.
                    </p>
                    <CodeBlock>
                        <CodeText type="param">@lazy</CodeText>
                        <br />
                        <CodeText type="keyword">function</CodeText>{" "}
                        <CodeText type="function">func</CodeText>
                        (text1, text2) {"{"} <br />
                        <Tab />
                        say{" "}
                        <CodeText type="string">"$text1 and $text2"</CodeText>;
                        <br />
                        {"}"}
                    </CodeBlock>
                </div>
                <section id="root" />
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Root
                    <SectionLinkCopy sectionId="root" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Ignore the class the function is in and directly add it
                        to root.
                    </p>
                    <CodeBlock>
                        <CodeText type="keyword">class</CodeText>{" "}
                        <CodeText type="class">MyClass</CodeText> {"{"}
                        <br />
                        <Tab />
                        <CodeText type="param">@root</CodeText>
                        <br />
                        <Tab />
                        <CodeText type="keyword">function</CodeText>{" "}
                        <CodeText type="function">func</CodeText>
                        () {"{"} <br />
                        <Tab />
                        <Tab />
                        say{" "}
                        <CodeText type="string">
                            "data/namespace/functions/func.mcfunction"
                        </CodeText>
                        <br />
                        <Tab />
                        <Tab />
                        <CodeText type="comment">
                            {"//"} NOT
                            data/namespace/functions/myclass/func.mcfunction
                        </CodeText>
                        ;
                        <br />
                        <Tab />
                        {"}"}
                        <br />
                        {"}"}
                    </CodeBlock>
                </div>
                <section id="if" />
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    If
                    <SectionLinkCopy sectionId="if" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Take a number constant. If the constant is 0, the
                        function will be created as an empty lazy function.
                        Otherwise, the function will be created as normal lazy
                        function. Note that an empty lazy function is still
                        callable, it just doesn't do anything.
                    </p>
                    <CodeBlock>
                        <CodeText type="param">@if(__DEBUG__)</CodeText>{" "}
                        <CodeText type="comment">
                            {"//"} #env __DEBUG__
                        </CodeText>
                        <br />
                        <CodeText type="keyword">function</CodeText>{" "}
                        <CodeText type="function">debug</CodeText>
                        (string) {"{"} <br />
                        <Tab />
                        say <CodeText type="number">$string</CodeText>;
                        <br />
                        {"}"}
                    </CodeBlock>
                    <p>
                        <Tab />
                        If a function is named <code>_</code>, it'll be
                        automatically called and deleted.
                    </p>
                </div>
            </section>
        </>
    );
};

export default Decorator;
