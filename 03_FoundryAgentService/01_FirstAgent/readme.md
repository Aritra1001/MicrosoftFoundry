How agents in general work and how it ties to foundry.

It always starts with an input - user messages, system events, messages from other agents.

These inputs will arrive to our agent which is coupled with a LLM. It has instructions and also in Foundry has the capability to work with foundry tools.

And then based on the input and the various features that the agent can use, we receive an output which can be again a message
from an agent or a structured output in the form of a table and so on.

Foundry agent service is the assembly line when it comes to building our agents.

A chat client - this is an Open AI compatible client that handles sending and receiving messages
A conversation (chat session) - this keeps track of the message history so that the agent remembers what you said
