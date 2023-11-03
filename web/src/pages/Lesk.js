import React, {useState} from 'react';
import './lesk.css'
import {JSONTree} from "react-json-tree";



const AmbigiousSentence = ({sentence, onSelect, selectedWord}) => {
    let tokens = ("" + sentence).split(' ')

    return (<p className="tokens" title="Select ambigious word">
        {tokens.map((token, idx) => (
            <React.Fragment>
                <span className={selectedWord == token ? "selected" : ""}
                      onClick={e => onSelect(token)}>{token}</span><span> </span>
            </React.Fragment>
        ))}
    </p>)
}

const SigHighlighter = ({sig, selectedWord, cleanedSentence}) => {

    return (
        <p>
            {
                sig && sig.map((word, index) => {
                    // Determine the className based on the word match
                    let className = '';
                    if (word === selectedWord) {
                        className = 'highlight-green';
                    } else if (cleanedSentence.includes(word)) {
                        className = 'highlight-red';
                    }

                    return (
                        <React.Fragment key={index}>
                            <span className={className}>{word}</span>
                            {index < sig.length - 1 ? ', ' : ''}
                        </React.Fragment>
                    );
                })
            }
        </p>
    );
};


const transformDataToHierarchy = (data) => {
    // Helper function to add hypernyms and hyponyms to the node
    const addHyponymsAndHypernyms = (node, data) => {
        node.children = [];

        // Add hypernyms
        if (data.hypernyms && data.hypernyms.length > 0) {
            for (const hypernym of data.hypernyms) {
                node.children.push({
                    name: hypernym.sense,
                    definition: hypernym.definition,
                    children: []
                });
            }
        }

        // Add hyponyms
        if (data.hyponyms && data.hyponyms.length > 0) {
            for (const hyponym of data.hyponyms) {
                node.children.push({
                    name: hyponym.sense,
                    definition: hyponym.definition,
                    children: []
                });
            }
        }
    };

    // The root node
    let rootNode = {
        name: "Word Senses",
        children: []
    };

    // Iterate through each sense and construct a hierarchical node
    for (const sense of data) {
        let node = {
            name: sense.sense,
            definition: sense.definition,
            children: []
        };

        // Add hypernyms and hyponyms as children
        addHyponymsAndHypernyms(node, sense);

        // Add node to root's children
        rootNode.children.push(node);
    }

    return rootNode;
};

const Lesk = () => {
    const [sentence, setSentence] = useState('');
    const [selectedWord, setSelectedWord] = useState(null);
    const [leskType, setLeskType] = useState('basic_lesk');

    const [definition, setDefinition] = useState(null);
    const [sense, setSense] = useState(null);
    const [cleanedSentence, setCleanedSentence] = useState(null);
    const [wordInfo, setWordInfo] = useState(null);
    const [origSig, setOrgSig] = useState([]);
    const [relSig, setRelSig] = useState([]);
    const [hierarchicalData, setHierarchicalData] = useState(null);

    const apiBase = process.env.REACT_APP_API_BASE_URL;

    const handleSentenceChange = (event) => {
        setSentence(event.target.value);
        setSelectedWord(null);
        setDefinition(null);
        setSense(null);
        setCleanedSentence(null);
    };
    const handleSearch = () => {
        setSelectedWord(null);
    };

    const onWordSelect = (word) => {
        setSelectedWord(word)
    }

    const findSense = async (lesk_type) => {
        const apiUrl = apiBase + `/${lesk_type}`;

        const postData = {
            context_sentence: sentence,
            ambiguous_word: selectedWord
        };

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(postData)
            });
            const data = await response.json();

            // Assuming the API returns data in the format: {definition: "some definition", sense: "some sense"}
            setSense(data.sense);
            setDefinition(data.definition);
            setCleanedSentence(data.cleanedSentence);

            if (lesk_type == 'extended_lesk') {
                setOrgSig(data.original_signature)
                setRelSig(data.related_signature)
            } else {
                setOrgSig([])
                setRelSig([]);
            }
        } catch (error) {
            console.error("Error fetching data:", error);
        }

        try {
            const response = await fetch(apiBase + `/word_info/${selectedWord}`);
            const data = await response.json();
            setWordInfo(data);

            const hierarchy = transformDataToHierarchy(data);
            setHierarchicalData(hierarchy)
        } catch (error) {
            console.error('Error fetching word info:', error);
        }
    };

    return (
        <div className="lesk">
            <div className="search-container mt-5 mb-5">
                <div className="input-group mb-3">
                    <input
                        type="text"
                        className="form-control sentence-input"
                        placeholder="Enter sentence..."
                        value={sentence}
                        onChange={handleSentenceChange}
                    />
                </div>
            </div>
            <div className="sentence-container">
                <AmbigiousSentence sentence={sentence} onSelect={onWordSelect} selectedWord={selectedWord}/>
                {selectedWord && (
                    <div className="mt-3 mb-3">
                        <div className="form-check">
                            <input
                                className="form-check-input"
                                type="radio"
                                name="leskTypeOptions"
                                id="basicLesk"
                                value="basic_lesk"
                                checked={leskType === 'basic_lesk'}
                                onChange={() => setLeskType('basic_lesk')}
                            />
                            <label className="form-check-label" htmlFor="basicLesk">Basic Lesk</label>
                        </div>
                        <div className="form-check">
                            <input
                                className="form-check-input"
                                type="radio"
                                name="leskTypeOptions"
                                id="extendedLesk"
                                value="extended_lesk"
                                checked={leskType === 'extended_lesk'}
                                onChange={() => setLeskType('extended_lesk')}
                            />
                            <label className="form-check-label" htmlFor="extendedLesk">Extended Lesk</label>
                        </div>
                        <div className="mt-3">
                            <button
                                className="btn m-1 btn-success"
                                onClick={() => findSense(leskType)}
                            >
                                Find Sense
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {definition && sense && (
                <div className="bg-light p-5 rounded-lg defination-container mb-5">
                    <h3>Sense: {sense}</h3>
                    <p className="lead">{definition}</p>
                    <hr/>
                    {
                        origSig && origSig.length > 0 && (
                            <div className="card mb-2">
                                <div className="card-body">
                                    <h5 className="card-title">Original Signature</h5>
                                    <SigHighlighter sig={origSig} cleanedSentence={cleanedSentence}
                                                    selectedWord={selectedWord}/>
                                </div>
                            </div>

                        )
                    }
                    {
                        relSig && origSig.length > 0 && (
                            <div className="card mb-2">
                                <div className="card-body">
                                    <h5 className="card-title">Related Signature from Hypernym and Hyponyms</h5>
                                    <SigHighlighter sig={relSig} cleanedSentence={cleanedSentence}
                                                    selectedWord={selectedWord}/>
                                </div>
                            </div>
                        )
                    }
                </div>
            )}

            {wordInfo && (
                <div className="bg-light p-5 rounded-lg defination-container mb-5">
                    <div className="card">
                        <div className="card-body">
                            <h5 className="card-title">Word Info</h5>
                            <div className="align-self-start w-100">
                                <JSONTree data={wordInfo}/>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Lesk;