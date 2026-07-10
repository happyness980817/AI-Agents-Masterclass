from typing import cast

from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel


class ContentPipelineState(BaseModel):

    # Inputs
    content_type: str = ""
    topic: str = ""

    # Internal
    max_length: int = 0
    score: int = 0

    # Content
    blog_post: str = ""
    tweet: str = ""
    linkedin_post: str = ""


class ContentPipelineFlow(Flow[ContentPipelineState]):

    @property
    def typed_state(self) -> ContentPipelineState:
        return cast(ContentPipelineState, self.state)

    @start()
    def init_content_pipeline(self):
        if self.typed_state.content_type not in ["tweet", "blog", "linkedin"]:
            raise ValueError("Wrong content type.")

        if self.topic == "":  # Just to validate that we passed a topic as an input.
            raise ValueError("The topic can't be blank")

        if self.typed_state.content_type == "tweet":
            self.typed_state.max_length = 150
        elif self.typed_state.content_type == "blog":
            self.typed_state.max_length = 800
        elif self.typed_state.content_type == "linkedin":
            self.typed_state.max_length = 500

    @listen(init_content_pipeline)
    def conduct_research(self):
        print("Researching...")
        return True

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
        # If a blog post has been make, show the old one to the AI and ask it to improve the post.
        # Else, just ask it to create one.
        print("Writing a blog post...")

    @listen(or_("make_tweet", "remake_tweet"))
    def handle_make_tweet(self):
        # If a tweet has been make, show the old one to the AI and ask it to improve the tweet.
        # Else, just ask it to create one.
        print("Writing a tweet post...")

    @listen(or_("make_linkedin_post", "remake_linkedin_post"))
    def handle_make_linkedin(self):
        # If a linkedin post has been make, show the old one to the AI and ask it to improve the post.
        # Else, just ask it to create one.
        print("Writing a linkedin post...")

    @listen(handle_make_blog)
    def check_seo(self):
        print("Checking Blog SEO...")

    @listen(or_(handle_make_tweet, handle_make_linkedin))
    def check_virality(self):
        print("Checking Virality...")

    @router(or_(check_seo, check_virality))
    def score_router(self):

        content_type = self.typed_state.content_type
        score = self.typed_state.score

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

# flow.kickoff(
#     inputs={
#         "content_type": "tweet",
#         "topic": "AI Dog Training",
#     },
# )
