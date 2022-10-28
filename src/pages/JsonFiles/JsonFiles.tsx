import React from "react";
import CodeBlock, { CodeText } from "../../components/CodeBlock";

const JsonFiles = () => {
    return (
        <>
            <section className="min-h-screen bg-secondary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
                <div className="text-secondary text-3xl md:text-6xl mx-auto">
                    JSON File
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Creating JSON files
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;Generate a formatted json file at desired
                        directory under the type using new keyword. Example of
                        json file types are <code>advancements</code>,{" "}
                        <code>item_modifiers</code>, <code>loot_tables</code>,
                        etc.
                    </p>
                    <CodeBlock>
                        <CodeText type="keyword">new</CodeText>{" "}
                        <CodeText type="class">file_type</CodeText>
                        (folder_name.file_name) {"{"}
                        <br />
                        &emsp;JSON content
                        <br />
                        {"}"}
                    </CodeBlock>
                    <p>Example:</p>
                    <CodeBlock>
                        <CodeText type="keyword">new</CodeText>{" "}
                        <CodeText type="class">advancements</CodeText>
                        (my_folder.first_join) {"{"}
                        <br />
                        &emsp;<CodeText type="string">"criteria"</CodeText>
                        <CodeText type="operator">:</CodeText> {"{"}
                        <br />
                        &emsp;&emsp;
                        <CodeText type="string">"requirement"</CodeText>
                        <CodeText type="operator">:</CodeText> {"{"}
                        <br />
                        &emsp;&emsp;&emsp;
                        <CodeText type="string">"trigger"</CodeText>
                        <CodeText type="operator">:</CodeText>{" "}
                        <CodeText type="string">"minecraft:tick"</CodeText>
                        <br />
                        &emsp;&emsp;{"}"}
                        <br />
                        &emsp;{"}"}
                        <CodeText type="operator">,</CodeText>
                        <br />
                        &emsp;<CodeText type="string">"rewards"</CodeText>
                        <CodeText type="operator">:</CodeText> {"{"}
                        <br />
                        &emsp;&emsp;
                        <CodeText type="string">"function"</CodeText>
                        <CodeText type="operator">:</CodeText>{" "}
                        <CodeText type="string">
                            "namespace:mydatapack/rejoin/first_join"
                        </CodeText>
                        <br />
                        &emsp;{"}"}
                        <br />
                        {"}"}
                    </CodeBlock>
                </div>
            </section>
        </>
    );
};

export default JsonFiles;
