import React, { ReactElement } from "react";
import { Link } from "react-router-dom";
import isDisplay from "../../utils/isDisplay";
import { scrollToHash, scrollToId } from "../../utils/scrollToHash";

export interface DocsLinkInterface {
    name: string;
    keyword: string;
    page: string;
    searchValue: string;
    sections?: ReactElement<DocsLinkInterface>[];
    hash?: string;
}

const DocsLink: React.FC<DocsLinkInterface> = (props) => {
    return (
        <div>
            {!props.sections ||
            props.sections!.some((DocsLink) => {
                return isDisplay(
                    DocsLink.props.name,
                    props.searchValue,
                    DocsLink.props.keyword
                );
            }) ? (
                <Link
                    to={
                        props.hash
                            ? `/documentation/${props.page}#${props.hash}`
                            : `/documentation/${props.page}`
                    }
                    className="text-white no-underline "
                    onClick={() => {
                        if (
                            props.hash &&
                            window.location.pathname ==
                                `/documentation/${props.page}`
                        )
                            setTimeout(() => {
                                scrollToId(props.hash!);
                            }, 100);
                    }}
                >
                    <p className="hover:text-gray-300 hover:scale-105">
                        {props.name}
                    </p>
                </Link>
            ) : (
                ""
            )}
            {props.sections?.map(
                (DocsLink, i) =>
                    isDisplay(
                        DocsLink.props.name,
                        props.searchValue,
                        DocsLink.props.keyword
                    ) && (
                        <div key={i} className="ml-4">
                            {DocsLink}
                        </div>
                    )
            )}
        </div>
    );
};

export default DocsLink;
