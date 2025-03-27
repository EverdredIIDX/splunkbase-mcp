from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any
import aiofiles
import os
from aiosplunkbase import SBClient
from aiosplunkbase.exceptions import AuthenticationError

SPLUNKBASE_USERNAME = os.environ.get("SPLUNKBASE_USERNAME")
SPLUNKBASE_PASSWORD = os.environ.get("SPLUNKBASE_PASSWORD")

if not SPLUNKBASE_USERNAME or not SPLUNKBASE_PASSWORD:
    raise ValueError("Missing Splunkbase credentials")

client = SBClient(SPLUNKBASE_USERNAME, SPLUNKBASE_PASSWORD)

# Create the MCP server
mcp = FastMCP("Splunkbase MCP", dependencies=["aiosplunkbase", "aiofiles"])

# Resources

@mcp.resource("app://{app}/info")
async def get_app_info(app: str | int) -> str:
    """Get detailed information about a Splunkbase app."""
    # If app can be an int, make sure it is an int
    try:
        app = int(app)
    except ValueError:
        pass

    info = await client.get_app_info(app)

    if info is None:
        return f"Error: App '{app}' not found"

    return str(info)


@mcp.resource("app://{app}/splunk_versions")
async def get_app_versions(app: str | int) -> str:
    """Get supported Splunk versions for an app."""
    # If app can be an int, make sure it is an int
    try:
        app = int(app)
    except ValueError:
        pass

    try:
        versions = await client.get_app_supported_versions(app)
        return f"Supported Splunk versions for {app}:\n" + "\n".join(versions)
    except Exception as e:
        return f"Error getting versions for {app}: {str(e)}"


# Tools

@mcp.tool()
async def search(ctx: Context, query: str) -> str:
    """
    Search Splunkbase for apps.
    
    Args:
        query: The search query to search Splunkbase for

    Returns:
        A list of results from the search
    """
    response = await client.search(query)
    ctx.info(f"Found {response.get('total', 0)} results for {query}")
    return response.get('results', [])


@mcp.tool()
async def get_app_latest_version(
    ctx: Context, app: str | int, splunk_version: str, is_cloud: bool = False
) -> Dict[str, Any]:
    """
    Get the latest compatible version of an app for a specific Splunk version.

    Args:
        app: The name or numeric ID of the Splunkbase app
        splunk_version: The Splunk version to check compatibility with
        is_cloud: Whether to check compatibility with Splunk Cloud

    Returns:
        Dictionary containing release information
    """
    # If app can be an int, make sure it is an int
    try:
        app = int(app)
    except ValueError:
        pass

    ctx.info(
        f"Finding latest version of {app} compatible with Splunk {splunk_version}"
    )

    try:
        release = await client.get_app_latest_version(
            app, splunk_version, is_cloud=is_cloud
        )
        return release
    except Exception as e:
        ctx.error(f"Error finding latest version: {str(e)}")
        raise


@mcp.tool()
async def download_app(
    ctx: Context,
    app: str | int,
    output_dir: str,
    version: Optional[str] = None,
) -> str:
    """
    Download a specific version of an app. If no version is specified, downloads the latest.

    Args:
        app: The name or numeric ID of the Splunkbase app
        output_dir: Directory to save the downloaded app
        version: Optional specific version to download

    Returns:
        Success message with download details
    """
    # If app can be an int, make sure it is an int
    try:
        app = int(app)
    except ValueError:
        pass

    try:
        await client.login()
    except AuthenticationError as e:
        ctx.error(f"Error logging in: {str(e)}")
        raise

    try:
        app_info = await client.get_app_info(app)
        app_name = app_info["appid"]
    except Exception as e:
        ctx.error(f"Error getting app info: {str(e)}")
        raise

    all_release_versions = [release["title"] for release in app_info["releases"]]
    if version and version not in all_release_versions:
        ctx.error(f"Version {version} not found for app {app_name}")
        raise ValueError(f"Version {version} not found for app {app_name}")

    try:
        ctx.info(
            f"Starting download of {app}" + (f" version {version}" if version else "")
        )

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Construct output filename
        output_file = os.path.join(
            output_dir, f"{app_name}_{version if version else 'latest'}.tgz"
        )

        total_size = 0
        async with aiofiles.open(output_file, "wb") as f:
            async for chunk in client.download_app(app, version):
                f.write(chunk)
                total_size += len(chunk)

        return f"Successfully downloaded {app} ({total_size} bytes) to {output_file}"

    except Exception as e:
        ctx.error(f"Error downloading app: {str(e)}")
        raise

 
# Prompts

@mcp.prompt()
def app_compatibility_check(app: str | int, splunk_version: str) -> str:
    """Create a prompt for checking app compatibility."""
    return f"""Please analyze the compatibility of the Splunkbase app '{app}' with Splunk version {splunk_version}.

First, check if the app exists using the check_app_exists tool.
Then, use the app://{app}/splunk_versions resource to see supported Splunk versions.
Finally, use get_app_latest_version to find the most compatible version.

Please provide:
1. Whether the app exists
2. List of supported Splunk versions
3. The recommended version to install
4. Any compatibility concerns or notes"""


if __name__ == "__main__":
    mcp.run()
