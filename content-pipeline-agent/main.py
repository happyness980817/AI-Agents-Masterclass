from typing import List, cast

from crewai.flow.flow import Flow, listen, start, router, and_, or_
from crewai import Agent
from crewai import LLM
from pydantic import BaseModel
from tools import web_search_tool
from seo_crew import SeoCrew
from virality_crew import ViralityCrew


class BlogPost(BaseModel):
    title: str
    subtitle: str
    sections: List[str]


class Tweet(BaseModel):
    content: str
    hashtags: str


class LinkedInPost(BaseModel):
    hook: str
    content: str
    call_to_action: str


class Score(BaseModel):

    score: int = 0
    reason: str = ""


class ContentPipelineState(BaseModel):

    # Inputs
    content_type: str = ""
    topic: str = ""

    # Internal
    max_length: int = 0
    research: str = ""
    score: Score | None = None

    # Content
    blog_post: BlogPost | None = None
    tweet: Tweet | None = None
    linkedin_post: LinkedInPost | None = None


class ContentPipelineFlow(Flow[ContentPipelineState]):

    @property
    def typed_state(self) -> ContentPipelineState:
        return cast(ContentPipelineState, self.state)

    @start()
    def init_content_pipeline(self):
        if self.typed_state.content_type not in ["tweet", "blog", "linkedin"]:
            raise ValueError("Wrong content type.")

        if (
            self.typed_state.topic == ""
        ):  # Just to validate that we passed a topic as an input.
            raise ValueError("The topic can't be blank")

        if self.typed_state.content_type == "tweet":
            self.typed_state.max_length = 150
        elif self.typed_state.content_type == "blog":
            self.typed_state.max_length = 800
        elif self.typed_state.content_type == "linkedin":
            self.typed_state.max_length = 500

    @listen(init_content_pipeline)
    def conduct_research(self):

        researcher = Agent(
            role="Head Researcher",
            backstory="You're like a digital detective who loves digging up fascinating facts and insights. You have a knack for finding the good stuff that others miss.",
            goal=f"Find the most interesting and useful info about {self.typed_state.topic}",
            tools=[web_search_tool],
        )

        research = researcher.kickoff(
            f"Find the most interesting and useful info about {self.typed_state.topic}"
        )
        self.typed_state.research = str(research)

    @router(conduct_research)
    def conduct_research_router(self):
        content_type = self.typed_state.content_type

        if content_type == "blog":
            return "make_blog_post"
        elif content_type == "tweet":
            return "make_tweet"
        else:
            return "make_linkedin_post"

    @listen(or_("make_blog_post", "remake_blog_post"))
    def handle_make_blog(self):
        # If a blog post has been made, show the old one to the AI and ask it to improve the post.
        # Else, just ask it to create one.

        blog_post = self.typed_state.blog_post

        llm = LLM(model="openai/o4-mini", response_format=BlogPost)

        if blog_post is None:
            self.typed_state.blog_post = llm.call(f"""
            Make a blog post with good SEO scores on the topic {self.typed_state.topic} using the following research:

            <research>
            ================
            {self.typed_state.research}
            ================
            </research>
            """)

        else:
            self.typed_state.blog_post = llm.call(f"""
            You wrote this blog post on {self.typed_state.topic}, but it does not have a good SEO score because of {self.typed_state.score.reason if self.typed_state.score else "it needs improvement"} 
            
            Improve it.

            <blog post>
            {self.typed_state.blog_post.model_dump_json()}
            </blog post>

            Use the following research.

            <research>
            ================
            {self.typed_state.research}
            ================
            </research>
            """)

    @listen(or_("make_tweet", "remake_tweet"))
    def handle_make_tweet(self):
        # If a tweet has been made, show the old one to the AI and ask it to improve the tweet.
        # Else, just ask it to create one.

        tweet = self.typed_state.tweet

        llm = LLM(model="openai/o4-mini", response_format=Tweet)

        if tweet is None:
            self.typed_state.tweet = llm.call(f"""
            Make a tweet that could go viral on the topic {self.typed_state.topic} using the following research:

            <research>
            ================
            {self.typed_state.research}
            ================
            </research>
            """)

        else:
            self.typed_state.tweet = llm.call(f"""
            You wrote this tweet on {self.typed_state.topic}, but it does not have a good virality score because of {self.typed_state.score.reason if self.typed_state.score else "it needs improvement"} 
            
            Improve it.

            <tweet>
            {self.typed_state.tweet.model_dump_json()}
            </tweet>

            Use the following research.

            <research>
            ================
            {self.typed_state.research}
            ================
            </research>
            """)

    @listen(or_("make_linkedin_post", "remake_linkedin_post"))
    def handle_make_linkedin(self):
        # If a linkedin post has been made, show the old one to the AI and ask it to improve the post.
        # Else, just ask it to create one.

        linkedin_post = self.typed_state.linkedin_post

        llm = LLM(model="openai/o4-mini", response_format=LinkedInPost)

        if linkedin_post is None:
            self.typed_state.linkedin_post = llm.call(f"""
            Make a blog post on the topic {self.typed_state.topic} using the following research:

            <research>
            ================
            {self.typed_state.research}
            ================
            </research>
            """)

        else:
            self.typed_state.linkedin_post = llm.call(f"""
            You wrote this linkedin post on {self.typed_state.topic}, but it does not have a good virality score because of {self.typed_state.score.reason if self.typed_state.score else "it needs improvement"} 
            
            Improve it.

            <linkedin post>
            {self.typed_state.linkedin_post.model_dump_json()}
            </linkedin post>

            Use the following research.

            <research>
            ================
            {self.typed_state.research}
            ================
            </research>
            """)

    @listen(handle_make_blog)
    def check_seo(self):
        print("Checking Blog SEO...")
        result = (
            SeoCrew()
            .crew()
            .kickoff(
                inputs={
                    "topic": self.typed_state.topic,
                    "blog_post": self.typed_state.blog_post.model_dump_json(),
                }
            )
        )
        self.typed_state.score = result.pydantic

    @listen(or_(handle_make_tweet, handle_make_linkedin))
    def check_virality(self):
        print("Checking Virality...")
        result = (
            ViralityCrew()
            .crew()
            .kickoff(
                inputs={
                    "topic": self.typed_state.topic,
                    "content_type": self.typed_state.content_type,
                    "content": (
                        self.typed_state.tweet.model_dump_json()
                        if self.typed_state.content_type == "tweet"
                        else self.typed_state.linkedin_post.model_dump_json()
                    ),
                }
            )
        )
        self.typed_state.score = result.pydantic

    @router(or_(check_seo, check_virality))
    def score_router(self):

        content_type = self.typed_state.content_type
        score = self.typed_state.score.score if self.typed_state.score else 0

        print(score)

        if score >= 8:
            return "check_passed"
        else:
            if content_type == "blog":
                return "remake_blog_post"
            elif content_type == "linkedin":
                return "remake_linkedin_post"
            else:
                return "remake_tweet"

    @listen("check_passed")
    def finalize_content(self):
        print("Finalizing Content...")


flow = ContentPipelineFlow()

flow.plot()

flow.kickoff(
    inputs={
        "content_type": "blog",
        "topic": "AI Dog Training",
    },
)
