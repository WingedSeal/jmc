import React from "react";
import CodeBlock, { CodeText } from "../../components/CodeBlock";
import { Tab } from "../../components/CodeBlock/CodeBlock";
import useScrollToHash from "../../utils/scrollToHash";
import { Link } from "react-router-dom";

const NBT = () => {
    useScrollToHash();
    return (
        <section className="min-h-screen bg-secondary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
            <div className="text-secondary text-3xl md:text-6xl mx-auto">
                NBT Operations
            </div>
            <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                <p>
                    <Tab />
                    NBT Element can act similar to a{" "}
                    <Link to="/documentation/variable">variable</Link>. JMC
                    provides shorten syntax for accessing NBT element.
                </p>
                <CodeBlock>
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>
                    <br />
                    <CodeText type="class">my_storage</CodeText>
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>
                    <br />
                    <CodeText type="class">my_namespace</CodeText>
                    <CodeText type="operator">:</CodeText>
                    <CodeText type="class">my_storage</CodeText>
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>
                    <br />
                    <CodeText type="class">[~,~,~]</CodeText>
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>
                    <br />
                    <CodeText type="class">@e[tag=entity]</CodeText>
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>
                </CodeBlock>
                <p>A path can be empty to access the root NBT.</p>
            </div>
            <section id="nbt_assignment" />

            <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                NBT Assignment
            </div>
            <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                <p>
                    <Tab />
                    Set an NBT Element to another NBT Element or a constant
                    value.
                </p>

                <CodeBlock>
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>{" "}
                    <CodeText type="operator">=</CodeText> [
                    <CodeText type="number">1</CodeText>
                    <CodeText type="operator">,</CodeText>{" "}
                    <CodeText type="number">2</CodeText>
                    <CodeText type="operator">,</CodeText>{" "}
                    <CodeText type="number">3</CodeText>];
                </CodeBlock>
                <CodeBlock>
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>{" "}
                    <CodeText type="operator">=</CodeText>{" "}
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">other_element</CodeText>;
                </CodeBlock>
            </div>
            <section id="nbt_operation" />
            <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                NBT Operation
            </div>
            <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                <p>
                    <Tab />
                    Perform nbt operations, with 4 available operations. An
                    operation works on both constant value and another NBT
                    Element.
                </p>
                <ul className="ml-4 md:ml-6 list-disc list-inside">
                    <li>
                        <code>{"<<"}</code> Append: Append to an array
                    </li>
                    <li>
                        <code>{">>"}</code> Prepend: Prepend to an array
                    </li>
                    <li>
                        <code>+=</code> Merge: Merge an NBT compound(JSObject)
                        with another
                    </li>
                    <li>
                        <code>^5</code> Insert: Insert an element into an array
                        at index
                    </li>
                </ul>
                <CodeBlock>
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>{" "}
                    <CodeText type="operator">+=</CodeText>{" "}
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">other_element</CodeText>;
                    <br />
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>{" "}
                    <CodeText type="operator">+=</CodeText> {"{key: value}"};
                </CodeBlock>
                <p>
                    <Tab />
                    To use operation with string instead, simply add{" "}
                    <code>[{"<start>:[<end>]"}]</code> at the end.
                </p>
                <CodeBlock>
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>{" "}
                    <CodeText type="operator">+=</CodeText>{" "}
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">other_element</CodeText>[1:5];
                    <br />
                    <CodeText type="comment">
                        {"// "}
                        data modify storage namespace:namespace path.to.element
                        merge string storage namespace:namespace
                        path.to.other_element 1 5
                    </CodeText>
                    <br />
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>{" "}
                    <CodeText type="operator">+=</CodeText>{" "}
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">other_element</CodeText>
                    [2:];
                </CodeBlock>
            </div>
            <section id="get_nbt" />
            <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                Get NBT
            </div>
            <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                <p>
                    <Tab />
                    To use <code>/data ... get</code>, for{" "}
                    <code>/execute store</code>, simply type the NBT Element.
                    This may be followed by <code>* {"<int>"}</code> for scaling
                </p>
                <CodeBlock>
                    execute store result score ... run{" "}
                    <CodeText type="class">@e[tag=entity]</CodeText>
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>;
                </CodeBlock>
                <CodeBlock>
                    execute store result score ... run{" "}
                    <CodeText type="class">@e[tag=entity]</CodeText>
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>{" "}
                    <CodeText type="operator">*</CodeText>{" "}
                    <CodeText type="number">5</CodeText>;
                </CodeBlock>
            </div>
            <section id="remove_nbt" />
            <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                Remove NBT
            </div>
            <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                <p>
                    <Tab />
                    To delete/remove and NBT Element, add <code>
                        .del()
                    </code>{" "}
                    after the NBT Element.
                </p>
                <CodeBlock>
                    <CodeText type="class">@e[tag=entity]</CodeText>
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="function">del</CodeText>();
                </CodeBlock>
            </div>
            <section id="execute_store" />
            <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                Execute store
            </div>
            <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                <CodeBlock>
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>{" "}
                    <CodeText type="operator">=</CodeText> {"<command>"};{" "}
                    <CodeText type="comment">
                        {"//"} execute store result ... int 1
                    </CodeText>
                    <br />
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>{" "}
                    <CodeText type="operator">=</CodeText> (
                    <CodeText type="class">{"<type>"}</CodeText>) {"<command>"};{" "}
                    <CodeText type="comment">
                        {"//"} execute store result ... type 1
                    </CodeText>
                    <br />
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>{" "}
                    <CodeText type="operator">=</CodeText>{" "}
                    <CodeText type="number">{"<scale>"}</CodeText>{" "}
                    <CodeText type="operator">*</CodeText> (
                    <CodeText type="class">{"<type>"}</CodeText>) {"<command>"};{" "}
                    <CodeText type="comment">
                        {"//"} execute store result ... type scale
                    </CodeText>
                    <br />
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>{" "}
                    <CodeText type="operator">?=</CodeText> {"<command>"};{" "}
                    <CodeText type="comment">
                        {"//"} execute store success
                    </CodeText>
                </CodeBlock>
                <p>
                    <Tab />
                    Example
                </p>
                <CodeBlock>
                    <CodeText type="operator">::</CodeText>
                    <CodeText type="param">path</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">to</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="param">element</CodeText>{" "}
                    <CodeText type="operator">=</CodeText> (
                    <CodeText type="class">float</CodeText>){" "}
                    <CodeText type="variable">$var</CodeText>;{" "}
                    <CodeText type="comment">
                        {"//"} execute store result storage namespace:namespace
                        path.to.element float 1 run scoreboard players get $var
                        __variable__
                    </CodeText>
                </CodeBlock>
            </div>
        </section>
    );
};

export default NBT;
