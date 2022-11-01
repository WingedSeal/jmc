import React from "react";
import CodeBlock, { CodeText } from "../../components/CodeBlock";
import { Tab } from "../../components/CodeBlock/CodeBlock";

const Header = () => {
    return (
        <>
            <section className="min-h-screen bg-primary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
                <div className="text-primary text-3xl md:text-6xl mx-auto">
                    Header (Preprocessing)
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Advanced configuration and preprocessing of JMC. Create
                        a file with the same name as your main JMC file but with{" "}
                        <code>.hjmc</code> extension. (The default is{" "}
                        <code>main.hjmc</code>)
                    </p>
                </div>

                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Macros
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Replace a keyword with another keyword
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#</CodeText>define replacement
                        original_keyword
                    </CodeBlock>
                    <p>
                        <Tab />
                        Example
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#</CodeText>define LOOP
                        __tick__
                    </CodeBlock>
                    <CodeBlock>
                        <CodeText type="keyword">function</CodeText>{" "}
                        <CodeText type="function">LOOP</CodeText>() {"{"}
                        <br />
                        <Tab />
                        say <CodeText type="string">"Run every tick"</CodeText>;
                        <br />
                        {"}"}
                    </CodeBlock>
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Credit
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Add comment to the end of every <code>
                            .mcfunction
                        </code>{" "}
                        file generated.
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#</CodeText>credit{" "}
                        <CodeText type="string">
                            This datapack is made by
                        </CodeText>
                        <br />
                        <CodeText type="operator">#</CodeText>credit
                        <br />
                        <CodeText type="operator">#</CodeText>credit{" "}
                        <CodeText type="string">WingedSeal</CodeText>
                    </CodeBlock>
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Include
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Add other header file
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#</CodeText>include{" "}
                        <CodeText type="string">"header_name"</CodeText>
                    </CodeBlock>
                    <CodeBlock>
                        <CodeText type="operator">#</CodeText>include{" "}
                        <CodeText type="string">{"<header_name>"}</CodeText>
                    </CodeBlock>
                </div>
                {/* <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    <s>Mod Commands</s>
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab/>Lorem ipsum dolor sit amet consectetur adipisicing
                        elit. Neque dolorum, quae, tenetur libero aut dicta nisi
                        cumque nemo beatae debitis voluptatum inventore quaerat
                        harum expedita fugit, alias quasi velit consequuntur?
                    </p>
                </div> */}
            </section>
        </>
    );
};

export default Header;
