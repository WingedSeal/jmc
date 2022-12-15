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
                    <p>
                        <Tab />
                        Semicolon is not required in <code>.hjmc</code> file.
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
                        <CodeText type="operator">#define</CodeText> replacement
                        original_keyword
                    </CodeBlock>
                    <p>
                        <Tab />
                        Example
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#define</CodeText> LOOP
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
                        <CodeText type="operator">#credit</CodeText>{" "}
                        <CodeText type="string">
                            "This datapack is made by"
                        </CodeText>
                        <br />
                        <CodeText type="operator">#credit</CodeText>
                        <br />
                        <CodeText type="operator">#credit</CodeText>{" "}
                        <CodeText type="string">"WingedSeal"</CodeText>
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
                        <CodeText type="operator">#include</CodeText>{" "}
                        <CodeText type="string">"header_name"</CodeText>
                    </CodeBlock>
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Mod/New Commands
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Make JMC recognize non-vanilla or new command so that it
                        doesn't throw an error when using your mod's command
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#command</CodeText>{" "}
                        my_mod_command
                    </CodeBlock>
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Override minecraft namespace
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Grant JMC the authority to fully control minecraft
                        namespace of the datapack. This will result in JMC
                        deleting minecraft namespace before it compiles. You'll
                        be able to edit it directly from jmc using{" "}
                        <code>minecraft</code> as a folder.
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#override_minecraft</CodeText>
                    </CodeBlock>
                    <p>
                        <Tab />
                        Example
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#override_minecraft</CodeText>
                    </CodeBlock>
                    <CodeBlock>
                        <CodeText type="keyword">new</CodeText>{" "}
                        <CodeText type="class">tags.functions</CodeText>
                        (minecraft.my_functions_tag) {"{"}
                        <br />
                        <Tab />
                        <CodeText type="string">"values"</CodeText>{" "}
                        <CodeText type="operator">=</CodeText> []
                        <br />
                        {"}"}
                    </CodeBlock>
                    <CodeBlock>
                        <CodeText type="keyword">function</CodeText>{" "}
                        <CodeText type="function">
                            minecraft.my_function
                        </CodeText>
                        () {"{"}
                        <br />
                        <Tab />
                        say{" "}
                        <CodeText type="string">
                            "This will be in minecraft namespace"
                        </CodeText>
                        ;
                        <br />
                        {"}"}
                    </CodeBlock>
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Static folder
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Make the compiler ignore a folder(in output) when
                        compiling resulting in that folder not getting deleted.
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#static</CodeText>{" "}
                        <CodeText type="string">
                            "folder_path_from_namespace_folder"
                        </CodeText>
                    </CodeBlock>
                </div>
            </section>
        </>
    );
};

export default Header;
