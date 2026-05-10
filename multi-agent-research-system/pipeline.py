from agents import build_research_agent, build_reading_agent, writer_chain, critic_chain

def run_research_pipeline(topic: str) -> dict:

    state = {}

    # search agent to gather initial research findings
    research_agent = build_research_agent()
    research_result = research_agent.invoke(
        {"messages": [
            ("user", f"Conduct research on the following topic and provide key findings:\n\n{topic}\n\nFocus on gathering relevant information, data, and insights that will help in understanding the topic comprehensively. Provide a summary of the key findings that can be used for deeper analysis.")
            ]
        }
    )
    state["research_findings"] = research_result["messages"][-1].content

    # reader agent

    reader_agent = build_reading_agent()
    reader_result = reader_agent.invoke({
        "messages": [
            ("user",
             f"""Based on the following search results about the '{topic}'
             pick the most relevent URL and scrape it for deeper content.\n\n
             Search Results : {state["research_findings"]}
             """)
        ]
    })

    state["scraped_content"] = reader_result["messages"][-1].content

    result_combined = (
        f"SEARCH RESULT: \n {state['research_findings']}\n\n"
        f"DETAILED SCRAPED CONTENT: \n{state['scraped_content']}"
    )

    writer_report = writer_chain.invoke({
        "topic": topic,
        "research": result_combined
    })
    state["report"] = writer_report

    critic_report = critic_chain.invoke({
        "topic": topic,
        "report": state["report"]
    })
    state["feedback"] = critic_report

    print(f"Report\n{state['report']}\n\n")
    print(f"Feedback:\n{state['feedback']}")


topic = input("Enter research topic")
run_research_pipeline(topic)