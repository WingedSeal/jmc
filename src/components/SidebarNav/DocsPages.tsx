import React, { ReactElement } from "react";
import DocsLink, { DocsLinkInterface } from "./DocsLink";

const getDocsPages = (
    searchValue: string
): ReactElement<DocsLinkInterface>[] => {
    return [
        <DocsLink
            name="Multiline Command"
            keyword=""
            page="multiline-command"
            searchValue={searchValue}
        />,
        <DocsLink
            name="Import"
            keyword="include copy"
            page="import"
            searchValue={searchValue}
        />,
        <DocsLink
            name="Comment"
            keyword="comments // #"
            page="comment"
            searchValue={searchValue}
        />,
        <DocsLink
            name="Function"
            keyword=""
            page="function"
            searchValue={searchValue}
            sections={[
                <DocsLink
                    name="Function defining"
                    keyword="define"
                    page="function"
                    hash="function_defining"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Function calling"
                    keyword=""
                    page="function"
                    hash="function_calling"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Anonymous Function"
                    keyword="arrow hidden execute"
                    page="function"
                    hash="anonymous_function"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Execute Expand"
                    keyword="copy paste hardcode"
                    page="function"
                    hash="execute_expand"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Class"
                    keyword="grouping layer folder"
                    page="function"
                    hash="class"
                    searchValue={searchValue}
                />,
            ]}
        />,
        <DocsLink
            name="Load/Tick"
            keyword="loop main json"
            page="load-tick"
            searchValue={searchValue}
        />,
        <DocsLink
            name="Variable"
            keyword="loop main json"
            page="variable"
            searchValue={searchValue}
            sections={[
                <DocsLink
                    name="Variable Assignment"
                    keyword="= equal set initialize"
                    page="variable"
                    hash="variable_assignment"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Variable Operation"
                    keyword="+=-=*=/=%=><??= null coalescing coalesce maximum minimum operator addition subtraction modulus multiply multiplication division divide assignment set swap math"
                    page="variable"
                    hash="variable_operation"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Incrementation"
                    keyword="decrementation"
                    page="variable"
                    hash="variable_incrementation"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Get variable"
                    keyword="nbt"
                    page="variable"
                    hash="get_variable"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Convert to string"
                    keyword="formatted toString"
                    page="variable"
                    hash="convert_to_string"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Execute Store"
                    keyword="?= result success nbt"
                    page="variable"
                    hash="execute_store"
                    searchValue={searchValue}
                />,
            ]}
        />,
        <DocsLink
            name="Flow Controls"
            keyword=""
            page="flow-controls"
            searchValue={searchValue}
            sections={[
                <DocsLink
                    name="Condition"
                    keyword=">= <= === matches if"
                    page="flow-controls"
                    searchValue={searchValue}
                    hash="condition"
                />,
                <DocsLink
                    name="Logical Operator"
                    keyword="logic gate and or not parenthesis disjunction discrete math"
                    page="flow-controls"
                    searchValue={searchValue}
                    hash="logical_operator"
                />,
                <DocsLink
                    name="If/Else"
                    keyword="elif"
                    page="flow-controls"
                    searchValue={searchValue}
                    hash="if_else"
                />,
                <DocsLink
                    name="If expand"
                    keyword="execute"
                    page="flow-controls"
                    searchValue={searchValue}
                    hash="if_expand"
                />,
                <DocsLink
                    name="While"
                    keyword="loop"
                    page="flow-controls"
                    searchValue={searchValue}
                    hash="while"
                />,
                <DocsLink
                    name="Do-While"
                    keyword="loop break"
                    page="flow-controls"
                    searchValue={searchValue}
                    hash="do_while"
                />,
                <DocsLink
                    name="For"
                    keyword="loop"
                    page="flow-controls"
                    searchValue={searchValue}
                    hash="for"
                />,
                <DocsLink
                    name="Switch Case"
                    keyword="optimization optimize binary search tree performance break default match"
                    page="flow-controls"
                    searchValue={searchValue}
                    hash="switch_case"
                />,
            ]}
        />,
        <DocsLink
            name="JSON Files"
            keyword="new advancements item_modifiers loot_tables tags"
            page="json-files"
            searchValue={searchValue}
        />,
        <DocsLink
            name="Built-in Function"
            keyword="feature"
            page="built-in-function"
            searchValue={searchValue}
        />,
        <DocsLink
            name="Decorator"
            keyword="decorate modify function"
            page="decorator"
            searchValue={searchValue}
            sections={[
                <DocsLink
                    name="Add"
                    keyword="called from tick"
                    page="decorator"
                    searchValue={searchValue}
                    hash="add"
                />,
                <DocsLink
                    name="Lazy"
                    keyword="replaced token define inline"
                    page="decorator"
                    searchValue={searchValue}
                    hash="lazy"
                />,
            ]}
        />,
        <DocsLink
            name="Header"
            keyword="feature hjmc preprocessor preprocessing configuration"
            page="header"
            searchValue={searchValue}
            sections={[
                <DocsLink
                    name="Macros"
                    keyword="replaced token define"
                    page="header"
                    searchValue={searchValue}
                    hash="define"
                />,
                <DocsLink
                    name="Binding"
                    keyword="special macro __uuid__ __namespace__ random generate auto"
                    page="header"
                    searchValue={searchValue}
                    hash="binding"
                />,
                <DocsLink
                    name="Credit"
                    keyword="comment end mcfunction"
                    page="header"
                    searchValue={searchValue}
                    hash="credit"
                />,
                <DocsLink
                    name="Include"
                    keyword="import copy"
                    page="header"
                    searchValue={searchValue}
                    hash="include"
                />,
                <DocsLink
                    name="Command"
                    keyword="new mod error create"
                    page="header"
                    searchValue={searchValue}
                    hash="command"
                />,
                <DocsLink
                    name="Delete"
                    keyword="ignore semicolons same command"
                    page="header"
                    searchValue={searchValue}
                    hash="del"
                />,
                <DocsLink
                    name="Override"
                    keyword="minecraft folder otehr namespace authority control directly"
                    page="header"
                    searchValue={searchValue}
                    hash="override"
                />,
                <DocsLink
                    name="Uninstall"
                    keyword="modify function"
                    page="header"
                    searchValue={searchValue}
                    hash="uninstall"
                />,
                <DocsLink
                    name="Static"
                    keyword="folder deleted"
                    page="header"
                    searchValue={searchValue}
                    hash="static"
                />,
                <DocsLink
                    name="Nometa"
                    keyword="pack.mcmeta static"
                    page="header"
                    searchValue={searchValue}
                    hash="nometa"
                />,
            ]}
        />,
    ];
};

export default getDocsPages;
