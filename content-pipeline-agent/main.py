from typing import cast

from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel


class ContentPipelineState(BaseModel):

    # Inputs
    content_type: str = ""
    topic: str = ""

    # Internal
    max_length: int = 0


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
    def router(self):
        content_type = self.typed_state.content_type

        if content_type == "blog":
            return "make_blog"
        elif content_type == "tweet":
            return "make_tweet"
        else:
            return "make_linkedin_post"

    @listen("make_blog")
    def handle_make_blog(self):
        print("Writing a blog post...")

    @listen("make_tweet")
    def handle_make_tweet(self):
        print("Writing a tweet post...")

    @listen("make_linkedin")
    def handle_make_linkedin(self):
        print("Writing a linkedin post...")

    @listen(handle_make_blog)
    def check_seo(self):
        print("Checking Blog SEO...")

    @listen(or_(handle_make_tweet, handle_make_linkedin))
    def check_virality(self):
        print("Checking Virality...")

    @listen(or_(check_seo, check_virality))
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
