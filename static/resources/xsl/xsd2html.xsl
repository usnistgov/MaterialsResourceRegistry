<?xml version="1.0" encoding="UTF-8"?>
<!--
################################################################################
#
# File Name: xsd2html.xsl
# Purpose: 	Renders an XML document in HTML
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################ 
 -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	version="1.0">
	<xsl:output method="html" indent="yes" encoding="UTF-8" />
	<xsl:preserve-space elements="*" />
	<xsl:template match="/">	 	
		<ul class="tree">
			<xsl:apply-templates />
		</ul>
	</xsl:template>
	<xsl:template match="*">		
		<xsl:choose>
			<!-- Nothing to do for these elements -->
			<xsl:when test="contains(name(.),'include')">
			</xsl:when>
			<xsl:when test="contains(name(.),'import')">
			</xsl:when>
			<xsl:when test="contains(name(.),'annotation')">
			</xsl:when>			
			<xsl:otherwise>
				<li>
				<div class="element-wrapper">
					<!-- no left indent for root element -->
					<xsl:if test="not(ancestor::*)">
						<xsl:attribute name="style">left:0</xsl:attribute>
					</xsl:if>	
					<span class="path">
						<xsl:value-of select="name(.)"/>
				        <xsl:variable name="vnumPrecSiblings" select="count(preceding-sibling::*[name()=name(current())])"/>
				        <xsl:if test="$vnumPrecSiblings">
				            <xsl:value-of select="concat('[', $vnumPrecSiblings +1, ']')"/>
				        </xsl:if>
					</span>
					<xsl:choose>
						<!-- Element with children -->
						<xsl:when test="*">
							<span class="collapse" style="cursor:pointer;" onclick="showhide(event);"></span>
							<span class="category">	
								<xsl:choose>
									<xsl:when test="contains(name(.),'sequence')">																		
										<span onclick="showMenuSequence(event)" style="cursor:pointer;">																								
											<xsl:value-of select="name(.)" />
										</span>
									</xsl:when>
									<xsl:when test="contains(name(.),'choice')">																		
										<span onclick="showMenuSequence(event)" style="cursor:pointer;">																								
											<xsl:value-of select="name(.)" />
										</span>
									</xsl:when>								
									<xsl:otherwise>
										<span>
											<xsl:value-of select="name(.)" />
										</span>
									</xsl:otherwise>						
								</xsl:choose>						
								<xsl:choose>
									<xsl:when test="./@name">
									<span class="type">
										<xsl:value-of select="@name" />
									</span>
									</xsl:when>
								</xsl:choose>
							</span>
						</xsl:when>
						<!-- Element without children -->					
						<xsl:otherwise>
							<span class="element">
								<xsl:choose>
									<xsl:when test="contains(name(.),'sequence')">
										<span onclick="showMenuSequence(event)" style="cursor:pointer;">
											<xsl:value-of select="name(.)" />
										</span>
									</xsl:when>
									<xsl:when test="contains(name(.),'element')">
										<span onclick="showMenuElement(event)" style="cursor:pointer;">
											<xsl:value-of select="name(.)" />
											<xsl:text> : </xsl:text>
										</span>
									</xsl:when>
									<xsl:when test="contains(name(.),'enumeration')">
										<span>
											<xsl:value-of select="name(.)" />
											<xsl:text> : </xsl:text>
											<span class="text">
												<xsl:value-of select="@value" />
											</span>											
										</span>
									</xsl:when>
									<xsl:otherwise>
										<span>
											<xsl:value-of select="name(.)" />
										</span>
									</xsl:otherwise>						
								</xsl:choose>						
							</span>
						</xsl:otherwise>
					</xsl:choose>
					<xsl:choose>
						<xsl:when test="not(*)">					
							<xsl:choose>
								<xsl:when test="./@name">
								<span class="name">
									<xsl:value-of select="@name" />
								</span>
								</xsl:when>
							</xsl:choose>
							<xsl:choose>
								<xsl:when test="./@type">
								<span class="type">
									<xsl:value-of select="@type" />
								</span>
								</xsl:when>
							</xsl:choose>
							<xsl:choose>
								<xsl:when test="./@ref">
								<span class="type">
									<xsl:value-of select="@ref" />
								</span>
								</xsl:when>
							</xsl:choose>
							<xsl:if test="contains(name(.),'element')"> 
								<span class="occurs">(
								<xsl:choose>
									<xsl:when test="./@minOccurs">
										<xsl:value-of select="@minOccurs" />								
									</xsl:when>
									<xsl:otherwise>
									1								
									</xsl:otherwise>
								</xsl:choose>
								, 
								<xsl:choose>
									<xsl:when test="./@maxOccurs">
										<xsl:choose>
											<xsl:when test="./@maxOccurs='unbounded'">
											*
											</xsl:when>
											<xsl:otherwise>
												<xsl:value-of select="@maxOccurs" />
											</xsl:otherwise> 
										</xsl:choose>
									</xsl:when>
									<xsl:otherwise>
									1
									</xsl:otherwise>
								</xsl:choose>
								)
								</span>
							</xsl:if>
						</xsl:when>
						<xsl:otherwise>
							<ul>
								<xsl:apply-templates />
							</ul>
						</xsl:otherwise>				
					</xsl:choose>
				</div>
				</li>
			</xsl:otherwise>
		</xsl:choose>		
	</xsl:template>
</xsl:stylesheet>

